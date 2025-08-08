from datetime import timedelta
import io
import logging
import os
import requests
import zipfile

import pandas as pd
from marshmallow import ValidationError

from extensions import db
from schemas.load_real_time_actual import LoadRealTimeActualValidation
from models.load_real_time_actual import LoadRealTimeActualModel

logger = logging.getLogger(__name__)

def scrape_load_real_time_actual(daterange):
    year_months_days = set()

    # Get unique year, month, day combos of query
    for date in daterange:
        year_months_days.add((date.year, date.strftime("%m"), date.strftime("%d")))
    
    # Get list of filenames that contain datetimes in query
    valid_filenames = []
    for date in year_months_days:
        valid_filenames.append(str(date[0]) + str(date[1]) + str(date[2]) + "pal.csv")

    # Get unique year, month combos of query
    year_months = set()
    for date in year_months_days:
        year_months.add((date[0], date[1]))

    # Make a list of URLs that will need to be accessed from year and month combos
    urls = []
    for date in year_months:
        urls.append('https://mis.nyiso.com/public/csv/pal/' + str(date[0]) + str(date[1]) + '01pal_csv.zip')

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

                    # Merge new data
                    data = pd.concat([data,df], axis=0)

                    # Delete CSV file after processing
                    os.remove(os.path.join('mydataset', filename))

    #Convert records into the correct format
    expected_cols = {
    'Time Stamp': 'timestamp',
    'PTID': 'ptid',
    'Name': 'name',
    'Load': 'load',
    }

    available_cols = {old: new for old, new in expected_cols.items() if old in data.columns}
    renamed_data = data.rename(columns=available_cols)
    records = renamed_data[list(available_cols.values())].to_dict(orient="records")

    try:
        validated_records = LoadRealTimeActualValidation().load(records, many=True)
    except ValidationError as err:
        print(err.messages)
    
    events = [LoadRealTimeActualModel(**record) for record in validated_records]
    
    db.session.add_all(events)
    db.session.commit()

    


                