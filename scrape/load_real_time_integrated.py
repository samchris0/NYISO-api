from datetime import timedelta
import io
import logging
import os
import requests
import zipfile

import pandas as pd
from marshmallow import ValidationError
from sqlalchemy.dialects.postgresql import insert

from nyiso_api.extensions import db
from nyiso_api.schemas.load_real_time_integrated import LoadRealTimeIntegratedValidation
from nyiso_api.models.load_real_time_integrated import LoadRealTimeIntegratedModel

logger = logging.getLogger(__name__)

def scrape_load_real_time_integrated(daterange):
    year_months_days = set()

    # Get unique year, month, day combos of query
    for date in daterange:
        year_months_days.add((date.year, date.strftime("%m"), date.strftime("%d")))
    
    # Get list of filenames that contain datetimes in query
    valid_filenames = []
    for date in year_months_days:
        valid_filenames.append(str(date[0]) + str(date[1]) + str(date[2]) + "palIntegrated.csv")

    # Get unique year, month combos of query
    year_months = set()
    for date in year_months_days:
        year_months.add((date[0], date[1]))

    # Make a list of URLs that will need to be accessed from year and month combos
    urls = []
    for date in year_months:
        urls.append('https://mis.nyiso.com/public/csv/palIntegrated/' + str(date[0]) + str(date[1]) + '01palIntegrated_csv.zip')

    data = pd.DataFrame()

    for url in urls:

        response = requests.get(url)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            for filename in z.namelist():
                if filename in valid_filenames:
                    
                    # Extract file and load data
                    with z.open(filename) as csv_file:
                        df = pd.read_csv(
                            csv_file,
                            parse_dates=["Time Stamp"],
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
    'Integrated Load': 'integrated_load',
    }

    available_cols = {old: new for old, new in expected_cols.items() if old in data.columns}
    renamed_data = data.rename(columns=available_cols)
    records = renamed_data[list(available_cols.values())].to_dict(orient="records")

    try:
        validated_records = LoadRealTimeIntegratedValidation().load(records, many=True)
    except ValidationError:
        logger.exception("Real-time integrated load validation failed")
        raise

    if not validated_records:
        logger.info("No real-time integrated load records found for %s", sorted(daterange))
        return

    validated_records = list({
        (record["timestamp"], record["name"]): record
        for record in validated_records
    }.values())
    
    table = LoadRealTimeIntegratedModel.__table__
    chunk_size = 5_000
    try:
        for offset in range(0, len(validated_records), chunk_size):
            chunk = validated_records[offset:offset + chunk_size]
            statement = insert(table).values(chunk)
            statement = statement.on_conflict_do_update(
                index_elements=[table.c.timestamp, table.c.name],
                set_={
                    "ptid": statement.excluded.ptid,
                    "integrated_load": statement.excluded.integrated_load,
                },
            )
            db.session.execute(statement)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    


                
