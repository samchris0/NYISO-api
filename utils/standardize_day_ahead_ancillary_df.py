import pandas as pd

import logging

logger = logging.getLogger(__name__)

def detect_format(df):
    if {'Name', 'PTID'}.issubset(df.columns):
        return 'long'
    elif any('East' in col for col in df.columns): #in df.columns if col != 'timestamp'):
        return 'wide'
    else:
        return 'simple_timeseries'

def standardize_dataframe(df):
    fmt = detect_format(df)

    if fmt == 'long':
        expected_cols = {
                    'Time Stamp': 'timestamp',
                    'Name': 'name',
                    'PTID': 'ptid',
                    '10 Min Spinning Reserve ($/MWHr)': 'spinning_reserve_10min',
                    '10 Min Non-Synchronous Reserve ($/MWHr)': 'non_sync_reserve_10min',
                    '30 Min Operating Reserve ($/MWHr)': 'operating_reserve_30min',
                    'NYCA Regulation Capacity ($/MWHr)': 'regulation_capacity'
                    }
        df = df.rename(columns=expected_cols)
        return df

    elif fmt == 'wide':

        df_long = df.melt(
                        id_vars='Time Stamp',
                        var_name='region_variable',
                        value_name='value'
                    )
        
        df_long[['Name', 'variable']] = df_long['region_variable'].str.extract(r'^(.*?) (.*)$')
        
        df_long = df_long.drop(columns='region_variable')

        df_wide = df_long.pivot_table(
                    index=['Time Stamp', 'Name'],
                    columns='variable',
                    values='value'
                ).reset_index()
        
        expected_cols = {
                    'Time Stamp': 'timestamp',
                    'Name': 'name',
                    '10 Min Spinning Reserve ($/MWHr': 'spinning_reserve_10min',
                    '10 Min Non-Synchronous Reserve': 'non_sync_reserve_10min',
                    '30 Min Operating Reserve ($/MWH': 'operating_reserve_30min',
                    'Regulation ($/MWHr)': 'regulation_capacity'
                    }
        df_wide = df_wide.rename(columns=expected_cols)

        return df_wide

    elif fmt == 'simple_timeseries':
        # Rename columns to fit standard format
        df['name'] = 'NYISO'  
        expected_cols = {
                    'Time Stamp': 'timestamp',
                    '10 Min Spinning Reserve ($/MWHr': 'spinning_reserve_10min',
                    '10 Min Non-Synchronous Reserve': 'non_sync_reserve_10min',
                    '30 Min Operating Reserve ($/MWH': 'operating_reserve_30min',
                    'Regulation ($/MWHr)': 'regulation_capacity'
                    }
        df = df.rename(columns=expected_cols)
        return df

    else:
        raise ValueError("Unknown format: cannot standardize data")
    


"""
Historical RTC Ancillary

2014
East 10 Min Spinning Reserve ($/MWHr	East 10 Min Non-Synchronous Reserve	East 30 Min Operating Reserve ($/MWH	East Regulation ($/MWHr)	
West 10 Min Spinning Reserve ($/MWHr	West 10 Min Non-Synchronous Reserve	West 30 Min Operating Reserve ($/MWH	West Regulation ($/MWHr)	
NYCA Regulation Movement ($/MW)

2000
Time Stamp	10 Minute Spinning	10 Minute Non-Sync	30 Minute Operating Reserve	Regulation
"""


"""
Day Ahead Ancillary

2025
10 Min Spinning Reserve ($/MWHr)	10 Min Non-Synchronous Reserve ($/MWHr)	30 Min Operating Reserve ($/MWHr)	NYCA Regulation Capacity ($/MWHr)

2009
East 10 Min Spinning Reserve ($/MWHr	East 10 Min Non-Synchronous Reserve	East 30 Min Operating Reserve ($/MWH	East Regulation ($/MWHr)	
West 10 Min Spinning Reserve ($/MWHr	West 10 Min Non-Synchronous Reserve	West 30 Min Operating Reserve ($/MWH	West Regulation ($/MWHr)

2000
10 Min Spinning Reserve ($/MWHr	10 Min Non-Synchronous Reserve	30 Min Operating Reserve ($/MWH	Regulation ($/MWHr)
"""

"""
Real Time Ancillary

2025
10 Min Spinning Reserve ($/MWHr)	10 Min Non-Synchronous Reserve ($/MWHr)	30 Min Operating Reserve ($/MWHr)	NYCA Regulation Capacity ($/MWHr)	NYCA Regulation Movement ($/MW)

2010
East 10 Min Spinning Reserve ($/MWHr)	East 10 Min Non-Synchronous Reserve	East 30 Min Operating Reserve ($/MWH)	East Regulation ($/MWHr)	
West 10 Min Spinning Reserve ($/MWHr)	West 10 Min Non-Synchronous Reserve	West 30 Min Operating Reserve ($/MWH)	West Regulation ($/MWHr)
"""
