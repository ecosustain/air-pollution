import os, sys
import pandas as pd
from datetime import timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from backend.data.utils.utils import generate_date_range_df, ddmmyyyyhhmm_yyyymmddhhmm, string_to_float
from metadata.meta_data import stations

def join_files(path="../scraped_data", verbose=True):
    files = os.listdir(path)
    for station in stations:
        station_indicators = {}
        for file in files:
            if file.split("_")[0] == station:
                indicator = file.split("_")[1].lower()
                df = pd.read_csv(f"{path}/{file}",
                                 sep=";", skiprows=7, encoding="latin1")
                df.columns = ["date", "time", indicator.lower()]
                df['datetime'] = df['date'].values + " " + df['time'].values
                df.drop(['date', 'time'], axis=1, inplace=True)
                df['datetime'] = df['datetime'].map(ddmmyyyyhhmm_yyyymmddhhmm)
                
                mask = df['datetime'].dt.strftime('%H:%M') == '24:00' # Identify rows where time is 24:00
                df.loc[mask, 'datetime'] = df.loc[mask, 'datetime'] + timedelta(days=1)
                df.loc[mask, 'datetime'] = df.loc[mask, 'datetime'].dt.replace(hour=0, minute=0)

                df[indicator.lower()] = df[indicator.lower()].map(string_to_float)
                df.drop_duplicates(inplace=True)
                df.dropna(inplace=True)
                if indicator in station_indicators:
                    current_indicator_df = station_indicators[indicator]
                    station_indicators[indicator] = pd.concat([current_indicator_df, df])
                else:
                    station_indicators[indicator] = df
                os.remove(f"{path}/{file}")

        station_df = generate_date_range_df()

        for indicator in station_indicators:
            station_df = pd.merge(station_df, station_indicators[indicator], on="datetime", how="left").drop_duplicates()

        station_df.to_csv(f"{path}/{station}.csv", index=False)

if __name__ == "__main__":
    join_files()