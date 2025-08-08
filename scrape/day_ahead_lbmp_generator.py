from datetime import timedelta
import io
import logging
import os
import requests
import zipfile

import pandas as pd
from marshmallow import ValidationError

from extensions import db
from schemas.day_ahead_lbmp_generator import DayAheadLBMPGeneratorValidation
from models.day_ahead_lbmp_generator import DayAheadLBMPGeneratorModel

logger = logging.getLogger(__name__)

def scrape_day_ahead_lbmp_generator(daterange):
    """
    This function gets day ahead lbmp generator data from the NYISO archive and store requested data
    in the day ahead lbmp generator database

        Args:
            daterange (list, datetimes): List of missing datetimes to scrape
    """

    year_months_days = set()

    # Get unique year, month, day combos of query
    for date in daterange:
        year_months_days.add((date.year, date.strftime("%m"), date.strftime("%d")))
    
    # Get list of filenames that contain datetimes in query
    valid_filenames = []
    for date in year_months_days:
        valid_filenames.append(str(date[0]) + str(date[1]) + str(date[2]) + "damlbmp_gen.csv")

    # Get unique year, month combos of query
    year_months = set()
    for date in year_months_days:
        year_months.add((date[0], date[1]))

    # Make a list of URLs that will need to be accessed from year and month combos
    urls = []
    for date in year_months:
        urls.append('https://mis.nyiso.com/public/csv/damlbmp/' + str(date[0]) + str(date[1]) + '01damlbmp_gen_csv.zip')

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
                                    )
                    
                    # Merge new data
                    data = pd.concat([data,df], axis=0)

                    # Delete CSV file after processing
                    os.remove(os.path.join('mydataset', filename))

    #Convert records into the correct format
    expected_cols = {
    'Time Stamp': 'timestamp',
    'PTID': 'ptid',
    'Name': 'name',
    'LBMP ($/MWHr)': 'lbmp',
    'Marginal Cost Losses ($/MWHr)': 'marginal_cost_losses',
    'Marginal Cost Congestion ($/MWHr)': 'marginal_cost_congestion'
    }

    renamed_data = data.rename(columns=expected_cols)
    records = renamed_data[list(expected_cols.values())].to_dict(orient="records")

    try:
        validated_records = DayAheadLBMPGeneratorValidation().load(records, many=True)
    except ValidationError as err:
        print(err.messages)
    
    events = [DayAheadLBMPGeneratorModel(**record) for record in validated_records]
    
    db.session.add_all(events)
    db.session.commit()

    


                