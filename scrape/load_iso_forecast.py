from datetime import timedelta
import io
import logging
import os
import requests
import zipfile

import pandas as pd
from marshmallow import ValidationError

from extensions import db
from schemas.load_iso_forecast import LoadISOForecastValidation
from models.load_iso_forecast import LoadISOForecastModel

logger = logging.getLogger(__name__)

def scrape_load_iso_forecast(daterange):
    year_months_days = set()

    # Get unique year, month, day combos of query
    for date in daterange:
        year_months_days.add((date.year, date.strftime("%m"), date.strftime("%d")))
    
    # Get list of filenames that contain datetimes in query
    valid_filenames = []
    for date in year_months_days:
        valid_filenames.append(str(date[0]) + str(date[1]) + str(date[2]) + "isolf.csv")

    # Get unique year, month combos of query
    year_months = set()
    for date in year_months_days:
        year_months.add((date[0], date[1]))

    # Make a list of URLs that will need to be accessed from year and month combos
    urls = []
    for date in year_months:
        urls.append('https://mis.nyiso.com/public/csv/isolf/' + str(date[0]) + str(date[1]) + '01isolf_csv.zip')

    data = pd.DataFrame()

    for url in urls:

        response = requests.get(url)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            for filename in z.namelist():
                if filename in valid_filenames:
                    
                    # Extract file and load data
                    z.extract(filename, path='mydataset')
                    # ADD: parse 'Time Stamp' as datetime
                    df = pd.read_csv(os.path.join('mydataset', filename),
                                    parse_dates=['Time Stamp']
                                    ).fillna(0)
                    

                    df = df.melt(id_vars=['Time Stamp'], var_name='Name', value_name='Load')

                    # Merge new data
                    data = pd.concat([data,df], axis=0)

                    # Delete CSV file after processing
                    os.remove(os.path.join('mydataset', filename))

    #Convert records into the correct format
    expected_cols = {
    'Time Stamp': 'timestamp',
    'Name': 'name',
    'Load': 'load'
    }

    available_cols = {old: new for old, new in expected_cols.items() if old in data.columns}
    renamed_data = data.rename(columns=available_cols)
    records = renamed_data[list(available_cols.values())].to_dict(orient="records")

    try:
        validated_records = LoadISOForecastValidation().load(records, many=True)
    except ValidationError as err:
        print(err.messages)
    
    events = [LoadISOForecastModel(**record) for record in validated_records]
    
    db.session.add_all(events)
    db.session.commit()

    


                