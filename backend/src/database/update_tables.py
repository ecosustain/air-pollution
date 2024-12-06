import os
import pandas as pd
import tempfile
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

from metadata.meta_data import STATIONS, INDICATORS
from utils.utils import (ddmmyyyyhhmm_yyyymmddhhmm, string_to_float,
                         get_request_response, get_session_id)
from utils.db_utils import with_session


class UpdateData:
    """
    A class for updating data in the database and CSV files based on data collected from the CETESB Qualar
    platform.

    This class is responsible for:
    - Fetching and processing data from CSV files.
    - Retrieving external data using the CETESB Qualar API based on a date range.
    - Updating the database with the fetched data.
    - Updating the corresponding CSV files with the newly retrieved data.

    Attributes:
        qualar_session_id (str): The session ID used for interacting with the CETESB Qualar API.
    """

    def __init__(self) -> None:
        self.qualar_session_id = get_session_id()

    @with_session
    def update_data(self, session, data_directory="/app/data/collected_csvs"):
        """
        Updates data in the database and CSV files using the session passed from the decorator.
        The method will run inside a transaction, and any errors will trigger a rollback.
        """
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
                    df_to_update_csv = self.update_database(response_text, station, indicator, session)
                    print(f"Successful database update: {station} - {indicator} - up to {end_date}")
                    dfs_to_update_csv[indicator.lower()] = df_to_update_csv
            self.update_csv_file(df, dfs_to_update_csv, data_directory, file)

    def update_database(self, data, station, indicator, session):
        """
        Updates the database with data from the API response.
        """
        db_connection = session.get_bind()
        with tempfile.NamedTemporaryFile(mode='w+', delete=True) as file:
            file.write(data)
            file.flush()
            df_to_update_csv = self.update_measure_indicator_table(file.name, station, indicator,
                                                                db_connection)
            self.update_station_indicators_table(station, indicator, db_connection)
        return df_to_update_csv

    @staticmethod
    def get_dates_to_update(df):
        """
        Determines the start and end dates for updating data based on the latest datetime in the given DataFrame.

        This method checks the latest date in the 'datetime' column of the DataFrame and computes:
        - The start date as the next day after the most recent date if there are multiple occurrences of the latest date.
        - The end date as the day before the current date.

        Parameters:
            df (pandas.DataFrame): A DataFrame containing a 'datetime' column to determine the dates.

        Returns:
            tuple: A tuple containing two strings:
                - start_date (str): The formatted start date as "DD/MM/YYYY".
                - end_date (str): The formatted end date as "DD/MM/YYYY".
        """
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
        """
        Loads a CSV file from the specified directory into a pandas DataFrame.

        This method checks if the provided file is a CSV and if it contains a 'datetime' column. 
        If any of these conditions are not met, the method returns `None`.

        Parameters:
            directory (str): The directory path where the CSV file is located.
            file_name (str): The name of the CSV file to be loaded.

        Returns:
            pandas.DataFrame or None: 
                - A pandas DataFrame containing the data from the CSV file if valid.
                - `None` if the file is not a CSV or does not contain a 'datetime' column.
        """
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
        """
        Updates the measure_indicator table with data from the given CSV file and returns a DataFrame for CSV update.

        This method reads data from a CSV file, adjusts the columns and data, and inserts it into the 'measure_indicator' table 
        in the database. It also returns a DataFrame with the updated indicator data to be used for CSV file updates.

        Parameters:
            file_path (str): The path to the CSV file containing the data to be updated.
            station (str): The name of the station associated with the data.
            indicator (str): The indicator name for which data is being updated.
            db_connection (sqlalchemy.engine.base.Connection): The database connection to interact with the MySQL database.

        Returns:
            pandas.DataFrame: A DataFrame containing the adjusted data for the specified indicator, used for updating the CSV file
                              of the corresponding station.
        """
        df = pd.read_csv(file_path, sep=";", skiprows=7, encoding="latin1").dropna()
        df, df_to_update_csv = self.adjust_columns_and_data(df, station, indicator)
        df.to_sql('measure_indicator', con=db_connection, if_exists='append',
                    index=False, chunksize=1000)
        return df_to_update_csv

    @staticmethod
    def update_station_indicators_table(station, indicator, db_connection):
        """
        Updates the `station_indicators` table by inserting a record if it does not already exist.

        This method checks whether a specific combination of station and indicator exists in the `station_indicators` table.
        If it does not exist, the method inserts a new record with an empty description.

        Parameters:
            station (str): The name of the station for which the record should be updated.
            indicator (str): The name or identifier of the indicator for the record.
            db_connection (SQLAlchemy Engine): A SQLAlchemy connection object used to interact with the database.

        Returns:
            None
        """
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
        """
        Updates a CSV file with new data from the provided DataFrames.

        This method merges new data (from `dfs_to_update_csv`) with an existing DataFrame (`original_df`)
        on the 'datetime' column, and updates the CSV file with the merged data. It ensures that any missing
        values in the original DataFrame are filled with the new data.

        Parameters:
            original_df (pandas.DataFrame): The original DataFrame that contains the existing data to be updated.
            dfs_to_update_csv (dict): A dictionary where the keys are indicator names and the values are DataFrames
                                    containing the new data for each indicator, with 'datetime' as the index.
            directory (str): The directory where the CSV file is located.
            file_name (str): The name of the CSV file to be updated.

        Returns:
            None
        """
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
        """
        Adjusts the columns and data of a DataFrame for a specific station and indicator, 
        including renaming columns, converting values, and handling datetime adjustments.

        This method modifies the given DataFrame by:
        - Renaming the columns to 'date', 'time', and 'value'.
        - Adjusting the datetime format using `adjust_datetime_column`.
        - Converting the 'value' column from string to float format.
        - Assigning the station and indicator IDs.
        - Removing duplicates and rows with null values in the 'value' column.
        - Preparing a separate DataFrame (`df_to_update_csv`) with updated values to update the CSV.

        Parameters:
            df (pandas.DataFrame): The input DataFrame that contains the data to be adjusted.
            station (str): The name of the station associated with the data.
            indicator (str): The name of the indicator associated with the data.

        Returns:
            tuple: A tuple of two DataFrames:
                - The first DataFrame is the adjusted version of the input, with the 'datetime', 'value',
                'idStation', and 'idIndicator' columns, cleaned of null and duplicate values.
                - The second DataFrame (`df_to_update_csv`) contains the 'datetime' and the adjusted 'value' column 
                for updating the corresponding CSV file.
        """
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
        """
        This method combines the 'date' and 'time' columns into a single 'original_datetime' column, 
        converts the datetime format from "DD/MM/YYYY HH:MM" to "YYYY/MM/DD HH:MM", and adjusts any 
        '24:00' timestamps to the next day's '00:00'. The 'original_datetime' column is dropped after 
        the conversion, and the final result is a DataFrame with the adjusted 'datetime' column.

        Parameters:
            df (pandas.DataFrame): A DataFrame containing 'date' and 'time' columns that need to be 
                                adjusted and combined into a single datetime column.

        Returns:
            pandas.DataFrame: The original DataFrame with a new 'datetime' column, and the 'date' and 
                            'time' columns removed. If any '24:00' times are present, they will be 
                            adjusted to '00:00' of the following day.
        """
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
