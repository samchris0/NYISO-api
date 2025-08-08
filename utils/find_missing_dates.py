import datetime
import logging

from sqlalchemy import func, text, select, literal, union_all
from sqlalchemy.orm import aliased
from sqlalchemy.dialects import postgresql

from extensions import db
from utils.get_date_range import get_date_range

logger = logging.getLogger(__name__)

def find_missing_dates(start, end, table):
    expected_dates = get_date_range(start, end)

    # Find all existing datapoints in the given table
    existing = (
                db.session.query(table.timestamp)
                .filter(table.timestamp.between(start, end))
                .all()
            )

    # Create a set of existing dates
    existing_dates = {
        ts[0].date() for ts in existing 
    }

    logger.info(existing_dates)
    
    return expected_dates - existing_dates

"""def find_missing_dates(daterange, table):

    The purpose of this function is to return a list of start and end datetimes of gaps in the queried data
    using get_consecutive_sequences helper function
    
        Parameters:
            daterange (List, datetimes): Timestamps of data in requested range
            model (SQLAlchemy model class): model being queried
            
        Returns:
            dates (list): list of lists of missing datetimes

    datetime_selects = [
        select([literal(dt).label("timestamp")]) for dt in daterange
    ]
    series = union_all(*datetime_selects).alias("date_range")
    series_column = series.c.timestamp


    join_condition = getattr(table, 'timestamp') == series_column
    query = (
        db.session.query(series_column)
        .select_from(series)
        .outerjoin(table, join_condition)
        .filter(getattr(table, 'timestamp').is_(None))
        .order_by(series_column)
    )

    # List of timestamps without data
    results = [row[0] for row in query.all()]

    return results


def get_consecutive_sequences(datetimes):

    Finds consecutive datetime sequences in a list and returns their start and end times.

    Parameters:
        datetimes: A list of datetime objects.

    Returns:
        sequences: A list of tuples. Each tuple represents a consecutive sequence
        and contains the start and end datetime objects of that sequence.

    if not datetimes:
        return []

    sorted_datetimes = sorted(datetimes)

    sequences = []

    if len(datetimes) == 1:
        sequences.append((datetimes[0], datetimes[0]))
        return sequences
    
    current_sequence_start = sorted_datetimes[0]

    for i in range(1, len(sorted_datetimes)):
        time_difference = sorted_datetimes[i] - sorted_datetimes[i-1]
        
        # Check if the time difference is greater than one hour
        if time_difference > dt.timedelta(hours=1): 
            sequences.append((current_sequence_start, sorted_datetimes[i-1]))
            current_sequence_start = sorted_datetimes[i]

    # Add the last sequence
    sequences.append((current_sequence_start, sorted_datetimes[-1]))
    
    return sequences
"""