import os
import pandas as pd
import tempfile
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

from utils.credentials import LOGIN_MYSQL, PASSWORD_MYSQL
from metadata.meta_data import STATIONS, INDICATORS
from utils.utils import (ddmmyyyyhhmm_yyyymmddhhmm, string_to_float,
                         get_request_response, get_session_id)


class UpdateData:
    def __init__(self) -> None:
        self.qualar_session_id = get_session_id()

    def update_data(self, data_directory="./backend/data/collected_csvs"):
        session_id = self.qualar_session_id

        for file in os.listdir(data_directory):
            print(f"Updating: {file}")
            dfs_to_update_csv = {}
            df = self.get_df_from_csv(data_directory, file)
            if df is None:
                continue
            start_date, end_date = self.get_dates_to_update(df)
            station = file[:-4]
            for indicator in INDICATORS:
                response_text = get_request_response(session_id, start_date, end_date,
                                                        STATIONS[station][0], INDICATORS[indicator])
                if response_text is not None:
                    df_to_update_csv = self.update_database(response_text, station, indicator)
                    print(f"Successful database update: {station} - {indicator} - up to {end_date}")
                    dfs_to_update_csv[indicator.lower()] = df_to_update_csv
            self.update_csv_file(df, dfs_to_update_csv, data_directory, file)

    def update_database(self, data, station, indicator):
        db_url = f"mysql+pymysql://{LOGIN_MYSQL}:{PASSWORD_MYSQL}@localhost/poluicao"
        db_connection = create_engine(db_url)
        with tempfile.NamedTemporaryFile(mode='w+', delete=True) as file:
            file.write(data)
            file.flush()
            df_to_update_csv = self.update_measure_indicator_table(file.name, station, indicator,
                                                                db_connection)
            self.update_station_indicators_table(station, indicator, db_connection)
        return df_to_update_csv

    @staticmethod
    def get_dates_to_update(df):
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
        max_date = df['datetime'].dt.date.max()
        count_max_date = (df['datetime'].dt.date == max_date).sum()
        if count_max_date > 1:
            start_date = (max_date + pd.Timedelta(days=1)).strftime("%d/%m/%Y")
        else:
            start_date = max_date.strftime("%d/%m/%Y")
        end_date = (datetime.now().date() - timedelta(days=1)).strftime("%d/%m/%Y")
        return start_date, end_date

    @staticmethod
    def get_df_from_csv(directory, file_name):
        if not file_name.endswith(".csv"):
            return None
        file_path = os.path.join(directory, file_name)
        try:
            df = pd.read_csv(file_path)
            if 'datetime' not in df.columns:
                raise Exception
        except:
            df = None
        return df

    def update_measure_indicator_table(self, file_path, station, indicator, db_connection):
        df = pd.read_csv(file_path, sep=";", skiprows=7, encoding="latin1").dropna()
        df, df_to_update_csv = self.adjust_columns_and_data(df, station, indicator)
        df.to_sql('measure_indicator', con=db_connection, if_exists='append',
                    index=False, chunksize=1000)
        return df_to_update_csv

    @staticmethod
    def update_station_indicators_table(station, indicator, db_connection):
        id_station = STATIONS[station][0]
        id_indicator = INDICATORS[indicator]
        with db_connection.connect() as connection:
            try:
                exists_query = text("""
                    SELECT COUNT(*) FROM station_indicators 
                    WHERE idStation = :id_station AND idIndicator = :id_indicator
                """)
                result = connection.execute(exists_query, {'id_station': id_station, 'id_indicator': id_indicator})
                if result.scalar() == 0:
                    insert_query = text("""
                        INSERT INTO station_indicators (description, idStation, idIndicator) 
                        VALUES (:description, :id_station, :id_indicator)
                    """)
                    connection.execute(insert_query, {'description': "", 'id_station': id_station, 'id_indicator': id_indicator})
            except Exception as e:
                print(f"Error: {e}")

    @staticmethod
    def update_csv_file(original_df, dfs_to_update_csv, directory, file_name):
        for indicator, new_data in dfs_to_update_csv.items():
            original_df = pd.merge(original_df, new_data, on='datetime', how='outer', suffixes=('', '_new'))
            if f"{indicator}_new" in original_df.columns:
                original_df[indicator] = original_df[indicator].fillna(original_df[f"{indicator}_new"])
                original_df.drop(columns=[f"{indicator}_new"], inplace=True)
        csv_file_path = os.path.join(directory, file_name)
        try:
            original_df.to_csv(csv_file_path, index=False)
            print(f"Succesfully updated {file_name}.")
        except:
            print(f"Failure while updating {file_name}.")

    def adjust_columns_and_data(self, df, station, indicator):
        df.columns = ["date", "time", "value"]
        df = self.adjust_datetime_column(df)
        df["value"] = df["value"].map(string_to_float)
        df['idStation'] = STATIONS[station][0]
        df['idIndicator'] = INDICATORS[indicator]
        df.drop_duplicates(inplace=True)
        df = df[df['value'].notnull()]
        df['value'] = df['value'].astype(float)

        df_to_update_csv = df[['datetime', 'value']].copy() # will be used for updating the csv file
        df_to_update_csv.rename(columns={'value': indicator.lower()}, inplace=True)
        return df.dropna(), df_to_update_csv.dropna()

    @staticmethod
    def adjust_datetime_column(df):
        df['original_datetime'] = df['date'].values + " " + df['time'].values
        df.drop(['date', 'time'], axis=1, inplace=True)
        df['original_datetime'] = df['original_datetime'].map(ddmmyyyyhhmm_yyyymmddhhmm)

        df['datetime'] = pd.to_datetime(df['original_datetime'], format='%Y/%m/%d %H:%M', errors='coerce')
        mask = df['datetime'].isna() & df['original_datetime'].str.endswith('24:00')
        df.loc[mask, 'datetime'] = pd.to_datetime(df.loc[mask, 'original_datetime'].str.replace('24:00', '00:00')) \
                                    + timedelta(days=1)
        df.drop(['original_datetime'], axis=1, inplace=True)
        return df


if __name__ == "__main__":
    UpdateData().update_data()
