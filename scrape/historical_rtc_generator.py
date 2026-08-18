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
from nyiso_api.schemas.historical_rtc_generator import HistoricalRTCGeneratorValidation
from nyiso_api.models.historical_rtc_generator import HistoricalRTCGeneratorModel

logger = logging.getLogger(__name__)

def scrape_historical_rtc_generator(daterange):
    
    """
    This function gets historical rtc generator data from the NYISO archive and store requested data
    in the historical rtc generator database

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
        valid_filenames.append(str(date[0]) + str(date[1]) + str(date[2]) + "hamlbmp_gen.csv")

    # Get unique year, month combos of query
    year_months = set()
    for date in year_months_days:
        year_months.add((date[0], date[1]))

    # Make a list of URLs that will need to be accessed from year and month combos
    urls = []
    for date in year_months:
        urls.append('https://mis.nyiso.com/public/csv/hamlbmp/' + str(date[0]) + str(date[1]) + '01hamlbmp_gen_csv.zip')

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
    'LBMP ($/MWHr)': 'lbmp',
    'Marginal Cost Losses ($/MWHr)': 'marginal_cost_losses',
    'Marginal Cost Congestion ($/MWH': 'marginal_cost_congestion'
    }
    
    renamed_data = data.rename(columns=expected_cols)
    records = renamed_data[list(expected_cols.values())].to_dict(orient="records")

    try:
        validated_records = HistoricalRTCGeneratorValidation().load(records, many=True)
    except ValidationError:
        logger.exception("Historical RTC generator validation failed")
        raise

    if not validated_records:
        logger.info("No historical RTC generator records found for %s", sorted(daterange))
        return

    validated_records = list({
        (record["timestamp"], record["ptid"]): record
        for record in validated_records
    }.values())
    
    table = HistoricalRTCGeneratorModel.__table__
    chunk_size = 5_000
    try:
        for offset in range(0, len(validated_records), chunk_size):
            chunk = validated_records[offset:offset + chunk_size]
            statement = insert(table).values(chunk)
            statement = statement.on_conflict_do_update(
                index_elements=[table.c.timestamp, table.c.ptid],
                set_={
                    "name": statement.excluded.name,
                    "lbmp": statement.excluded.lbmp,
                    "marginal_cost_losses": statement.excluded.marginal_cost_losses,
                    "marginal_cost_congestion": statement.excluded.marginal_cost_congestion,
                },
            )
            db.session.execute(statement)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    


                
