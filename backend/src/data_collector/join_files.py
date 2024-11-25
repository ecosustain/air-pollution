import os
import pandas as pd
from datetime import timedelta

from utils.utils import generate_date_range_df, ddmmyyyyhhmm_yyyymmddhhmm, string_to_float
from metadata.meta_data import STATIONS


def join_files(path="./backend/data/collected_csvs"):
    """
    Combines and processes CSV files for each station, generates a complete 
    time-series dataset, and saves the results to new station-specific CSV files.

    Parameters:
        path (str, optional): The directory path containing the collected CSV files. 
                              Defaults to "./backend/data/collected_csvs".

    Workflow:
        1. Iterates over all stations defined in `STATIONS`.
        2. Reads and processes all files associated with a station:
           - Extracts the indicator and loads the file into a DataFrame.
           - Creates a unified `datetime` column.
           - Cleans and adjusts incorrect rows.
           - Combines data from multiple files for the same indicator.
        3. Deletes processed files after merging their data.
        4. Generates a complete time-series DataFrame for the station.
        5. Merges all indicator data into the time-series DataFrame.
        6. Saves the resulting station-level dataset as a new CSV file.

    Returns:
        None
    """
    files = os.listdir(path)
    for station in STATIONS:
        station_indicators = {}
        for file in files:
            if file.split("_")[0] != station:
                continue
            indicator, df = get_indicator_and_df(path, file)
            df = create_datetime_column(df, indicator)
            df = adjust_incorrect_rows(df, indicator)
            if indicator in station_indicators:
                current_indicator_df = station_indicators[indicator]
                station_indicators[indicator] = pd.concat([current_indicator_df, df])
            else:
                station_indicators[indicator] = df
            os.remove(f"{path}/{file}")
        if station_indicators:
            max_date = get_maximum_date(station_indicators)
            station_df = generate_date_range_df(max_date)
            for indicator_df in station_indicators.values():
                station_df = pd.merge(station_df, indicator_df,
                                      on="datetime", how="left").drop_duplicates()
            station_df.to_csv(f"{path}/{station}.csv", index=False)


def get_maximum_date(station_indicators):
    """
    Retrieves the maximum datetime value across multiple DataFrames.

    Parameters:
        station_indicators (dict): A dictionary where keys are indicator names, and values are
                                   Pandas DataFrames containing a 'datetime' column.

    Returns:
        datetime: The maximum datetime value across all DataFrames.
    """
    max_dates = [df['datetime'].max() for df in station_indicators.values()]
    overall_max_date = max(max_dates)
    return overall_max_date


def get_indicator_and_df(path, file):
    """
    Extracts the indicator name and loads a DataFrame from a CSV file.

    Parameters:
        path (str): The directory path where the file is located.
        file (str): The file name, expected to follow a naming convention 
                    where the second part of the name (split by '_') corresponds to the indicator.

    Returns:
        tuple: A tuple containing:
               - indicator (str): The indicator name in lowercase.
               - df (pandas.DataFrame): The loaded DataFrame from the CSV file.
    """
    indicator = file.split("_")[1].lower()
    df = pd.read_csv(f"{path}/{file}", sep=";", skiprows=7, encoding="latin1")
    return indicator, df


def create_datetime_column(df, indicator):
    """
    Creates a `datetime` column in the DataFrame by combining `date` and `time` columns.

    Parameters:
        df (pandas.DataFrame): The input DataFrame with 'date' and 'time' columns.
        indicator (str): The name of the indicator, used as a column name in lowercase.

    Returns:
        pandas.DataFrame: The modified DataFrame with:
                          - A combined `datetime` column.
                          - Dropped `date` and `time` columns.
    """
    df.columns = ["date", "time", indicator.lower()]
    df['datetime'] = df['date'].values + " " + df['time'].values
    df.drop(['date', 'time'], axis=1, inplace=True)
    df['datetime'] = df['datetime'].map(ddmmyyyyhhmm_yyyymmddhhmm)
    return df


def adjust_incorrect_rows(df, indicator):
    """
    Adjusts incorrect rows in a DataFrame, handles invalid datetimes, 
    and converts indicator values to float format.

    Parameters:
        df (pandas.DataFrame): The input DataFrame with a `datetime` column and 
                               an indicator column.
        indicator (str): The name of the indicator, used as a column name in lowercase.

    Returns:
        pandas.DataFrame: The cleaned DataFrame with:
                          - Fixed invalid datetimes ending in "24:00" (shifted to the next day at "00:00").
                          - Converted indicator values to float format.
                          - Dropped duplicate and NaN rows.
    """
    df = df.rename(columns={'datetime': 'original_datetime'})
    df['datetime'] = pd.to_datetime(df['original_datetime'], format='%Y/%m/%d %H:%M', errors='coerce')
    mask = df['datetime'].isna() & df['original_datetime'].str.endswith('24:00')
    df.loc[mask, 'datetime'] = pd.to_datetime(df.loc[mask, 'original_datetime'].str.replace('24:00', '00:00')) \
                                + timedelta(days=1)
    df.drop(['original_datetime'], axis=1, inplace=True)
    df[indicator.lower()] = df[indicator.lower()].map(string_to_float)
    df.drop_duplicates(inplace=True)
    df.dropna(inplace=True)
    return df


if __name__ == "__main__":
    join_files()
