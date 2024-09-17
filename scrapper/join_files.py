import os, sys
import pandas as pd
from utils import generate_date_range_df, ddmmyyyyhhmm_yyyymmddhhmm, string_to_float
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from metadata.meta_data import stations

def join_files(path="./scrapper/scrapped_data", verbose=True):
    files = os.listdir(path)
    for station in stations:
        station_indicators = {}
        for file in files:
            if file.split("_")[0] == station:
                indicator = file.split("_")[1].lower()
                df = pd.read_csv(f"./scrapper/scrapped_data/{file}",
                                 sep=";", skiprows=7, encoding="latin1")
                df.columns = ["date", "time", indicator.lower()]
                df['datetime'] = df['date'].values + " " + df['time'].values
                df.drop(['date', 'time'], axis=1, inplace=True)
                df['datetime'] = df['datetime'].map(ddmmyyyyhhmm_yyyymmddhhmm)
                df[indicator.lower()] = df[indicator.lower()].map(string_to_float)
                df.drop_duplicates(inplace=True)
                df.dropna(inplace=True)
                if indicator in station_indicators:
                    current_indicator_df = station_indicators[indicator]
                    station_indicators[indicator] = pd.concat([current_indicator_df, df])
                else:
                    station_indicators[indicator] = df

        station_df = generate_date_range_df()

        for indicator in station_indicators:
            station_df = pd.merge(station_df, station_indicators[indicator], on="datetime", how="left").drop_duplicates()

        station_df.to_csv(f"./scrapper/stations_data/{station}.csv", index=False)


join_files()
