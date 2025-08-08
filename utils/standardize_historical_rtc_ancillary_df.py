import pandas as pd

import logging

logger = logging.getLogger(__name__)

def detect_format(df):
    if any('Movement' in col for col in df.columns):
        return 'movement'
    elif any('East' in col for col in df.columns): #in df.columns if col != 'timestamp'):
        return 'wide'
    else:
        return 'simple_timeseries'

def standardize_dataframe(df):
    fmt = detect_format(df)
    logger.info(fmt)

    if fmt == 'movement':
        movement = df[['Time Stamp','NYCA Regulation Movement ($/MW)']].copy()
        logger.info(movement.head())

        df.drop(columns=['NYCA Regulation Movement ($/MW)'], inplace=True)

        df_long = df.melt(
                        id_vars='Time Stamp',
                        var_name='region_variable',
                        value_name='value'
                    )
        
        logger.info(df_long.columns)

        df_long[['Name', 'variable']] = df_long['region_variable'].str.extract(r'^(.*?) (.*)$')
        
        df_long = df_long.drop(columns='region_variable')

        df_wide = df_long.pivot_table(
                    index=['Time Stamp', 'Name'],
                    columns='variable',
                    values='value'
                ).reset_index()
        
        df_wide.merge(movement, left_on='Time Stamp', right_on='Time Stamp')

        expected_cols = {
                    'Time Stamp': 'timestamp',
                    'Name': 'name',
                    '10 Min Spinning Reserve ($/MWHr': 'spinning_reserve_10min',
                    '10 Min Non-Synchronous Reserve': 'non_sync_reserve_10min',
                    '30 Min Operating Reserve ($/MWH': 'operating_reserve_30min',
                    'Regulation ($/MWHr)': 'regulation_capacity',
                    'NYCA Regulation Movement ($/MW)': 'regulation_movement'
                    }
        df_wide = df_wide.rename(columns=expected_cols)

        return df_wide
    
    elif fmt == 'wide':
        df_long = df.melt(
                        id_vars='Time Stamp',
                        var_name='region_variable',
                        value_name='value'
                    )
        
        logger.info(df_long.columns)

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
                    'Regulation ($/MWHr)': 'regulation_capacity',
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
                    'Regulation': 'regulation_capacity'
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



