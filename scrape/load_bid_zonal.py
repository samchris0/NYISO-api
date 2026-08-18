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
from nyiso_api.schemas.load_bid_zonal import LoadBidZonalValidation
from nyiso_api.models.load_bid_zonal import LoadBidZonalModel

logger = logging.getLogger(__name__)

def scrape_load_bid_zonal(daterange):
    year_months_days = set()

    # Get unique year, month, day combos of query
    for date in daterange:
        year_months_days.add((date.year, date.strftime("%m"), date.strftime("%d")))
    
    # Get list of filenames that contain datetimes in query
    valid_filenames = []
    for date in year_months_days:
        valid_filenames.append(str(date[0]) + str(date[1]) + str(date[2]) + "zonalBidLoad.csv")

    # Get unique year, month combos of query
    year_months = set()
    for date in year_months_days:
        year_months.add((date[0], date[1]))

    # Make a list of URLs that will need to be accessed from year and month combos
    urls = []
    for date in year_months:
        urls.append('https://mis.nyiso.com/public/csv/zonalBidLoad/' + str(date[0]) + str(date[1]) + '01zonalBidLoad_csv.zip')

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


    #Convert records into the correct format
    expected_cols = {
    'Time Stamp': 'timestamp',
    'PTID': 'ptid',
    'Name': 'name',
    'Energy Bid Load': 'energy_bid_load',
    'Bilateral Load': 'bilateral_load',
    'Price Cap Load': 'price_cap_load',
    'Virtual Load': 'virtual_load',
    'Virtual Supply': 'virtual_supply'
    }

    available_cols = {old: new for old, new in expected_cols.items() if old in data.columns}
    renamed_data = data.rename(columns=available_cols)
    records = renamed_data[list(available_cols.values())].to_dict(orient="records")

    try:
        validated_records = LoadBidZonalValidation().load(records, many=True)
    except ValidationError:
        logger.exception("Zonal load-bid validation failed")
        raise

    if not validated_records:
        logger.info("No zonal load-bid records found for %s", sorted(daterange))
        return

    validated_records = list({
        (record["timestamp"], record["ptid"]): record
        for record in validated_records
    }.values())
    
    table = LoadBidZonalModel.__table__
    chunk_size = 5_000
    try:
        for offset in range(0, len(validated_records), chunk_size):
            chunk = validated_records[offset:offset + chunk_size]
            statement = insert(table).values(chunk)
            statement = statement.on_conflict_do_update(
                index_elements=[table.c.timestamp, table.c.ptid],
                set_={
                    "name": statement.excluded.name,
                    "energy_bid_load": statement.excluded.energy_bid_load,
                    "bilateral_load": statement.excluded.bilateral_load,
                    "price_cap_load": statement.excluded.price_cap_load,
                    "virtual_load": statement.excluded.virtual_load,
                    "virtual_supply": statement.excluded.virtual_supply,
                },
            )
            db.session.execute(statement)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    


                
