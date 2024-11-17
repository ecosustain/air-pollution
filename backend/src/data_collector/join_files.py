import os
import pandas as pd
from datetime import timedelta

from utils.utils import generate_date_range_df, ddmmyyyyhhmm_yyyymmddhhmm, string_to_float
from metadata.meta_data import STATIONS


def join_files(path="./backend/data/collected_csvs"):
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
    max_dates = [df['datetime'].max() for df in station_indicators.values()]
    overall_max_date = max(max_dates)
    return overall_max_date


def get_indicator_and_df(path, file):
    indicator = file.split("_")[1].lower()
    df = pd.read_csv(f"{path}/{file}", sep=";", skiprows=7, encoding="latin1")
    return indicator, df


def create_datetime_column(df, indicator):
    df.columns = ["date", "time", indicator.lower()]
    df['datetime'] = df['date'].values + " " + df['time'].values
    df.drop(['date', 'time'], axis=1, inplace=True)
    df['datetime'] = df['datetime'].map(ddmmyyyyhhmm_yyyymmddhhmm)
    return df


def adjust_incorrect_rows(df, indicator):
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
