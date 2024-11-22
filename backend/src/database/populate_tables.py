import os
import pandas as pd
from sqlalchemy import create_engine
from backend.src.utils.credentials import LOGIN_MYSQL, PASSWORD_MYSQL
from backend.src.metadata.meta_data import STATIONS, INDICATORS, INDICATORS_DATA


def populate_tables():
    """
    Populates the 'stations', 'indicators', 'measure_indicator', and 'station_indicators' tables from CSV files.

    This function performs the following steps:
    1. Inserts data into the 'stations' and 'indicators' tables by calling the respective insert functions.
    2. Iterates over all CSV files in the specified directory (`CSV_DIRECTORY`), processes each file, 
       and inserts the data into the 'measure_indicator' and 'station_indicators' tables.

    Parameters:
        None

    Returns:
        None
    """
    CSV_DIRECTORY = './backend/data/collected_csvs'
    db_connection = create_engine(f"mysql+pymysql://{LOGIN_MYSQL}:{PASSWORD_MYSQL}@localhost/poluicao")
    insert_stations_data(db_connection)
    insert_indicators_data(db_connection)
    for file_name in os.listdir(CSV_DIRECTORY):
        if file_name.endswith('.csv'):
            file_path = os.path.join(CSV_DIRECTORY, file_name)
            station_name = file_name.replace(".csv", "")
            insert_data_from_station(file_path, station_name, db_connection)
    print("All files processed successfully.")


def insert_stations_data(db_connection):
    """
    Inserts data into the 'stations' table in the database.

    This function constructs a DataFrame from the `STATIONS` dictionary, which contains 
    station information (ID, name, latitude, and longitude). It then inserts this data into
    the `stations` table in the MySQL database. If the `stations` table already contains 
    data, the new records are appended.

    Parameters:
        db_connection (SQLAlchemy Connection): The active connection to the database 
        used for executing SQL operations.

    Returns:
        None
    """
    stations_data = {
        "id": [STATIONS[station][0] for station in STATIONS],
        "name": [station for station in STATIONS],
        "latitude": [STATIONS[station][1] for station in STATIONS],
        "longitude": [STATIONS[station][2] for station in STATIONS],
        "description": ["" for _ in STATIONS]  # Placeholder for description
    }
    stations_df = pd.DataFrame(stations_data)
    stations_df.to_sql('stations', con=db_connection, if_exists='append', index=False)


def insert_indicators_data(db_connection):
    """
    Inserts data into the 'indicators' table in the database.

    This function constructs a DataFrame from the `INDICATORS` and `INDICATORS_DATA` dictionaries, 
    which contain information about various pollutant indicators (ID, name, description, measurement unit, 
    and whether the indicator is considered a pollutant). It then inserts this data into the `indicators` 
    table in the MySQL database. If the `indicators` table already contains data, the new records are appended.

    Parameters:
        db_connection (SQLAlchemy Connection): The active connection to the database used for executing SQL
        operations.

    Returns:
        None
    """
    indicator_data = {
        "id": [INDICATORS[indicator] for indicator in INDICATORS],
        "name": [indicator.lower() for indicator in INDICATORS],
        "description": [INDICATORS_DATA[indicator_data][1] for indicator_data in INDICATORS_DATA],
        "measure_unit": [INDICATORS_DATA[indicator_data][2] for indicator_data in INDICATORS_DATA],
        "is_pollutant": [INDICATORS_DATA[indicator_data][0] for indicator_data in INDICATORS_DATA]
    }
    indicators_df = pd.DataFrame(indicator_data)
    indicators_df.to_sql('indicators', con=db_connection, if_exists='append', index=False)


def insert_data_from_station(file_path, station_name, db_connection):
    """
    Inserts data from a station's CSV file into the 'measure_indicator' and 'station_indicators' tables.

    This function processes a CSV file containing station data, adjusts the datetime format, 
    and then inserts the corresponding values into two database tables: 'measure_indicator' and 'station_indicators'.
    For each column in the CSV (excluding 'datetime'), it appends the data to the 'measure_indicator' table 
    and also updates the 'station_indicators' table with the station and indicator mappings.

    Parameters:
        file_path (str): The path to the CSV file containing the station data.
        station_name (str): The name of the station for which the data is being inserted.
        db_connection (SQLAlchemy Connection): A connection to the database where the data should be inserted.

    Returns:
        None
    """
    df = pd.read_csv(file_path)
    df['datetime'] = df['datetime'].apply(adjust_time_string)
    df['datetime'] = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%d %H:%M')

    station_indicators = {
        "idStation": [],
        "idIndicator": [],
        "description": [],
    }
    for col in df.columns:
        if col != 'datetime':
            station_indicators = append_to_station_indicators_dict(station_indicators, station_name, col)
            if append_to_measure_indicator_table(df, station_name, col, db_connection):
                print(f"{file_path} - {col} inserted into measure_indicator")
    append_to_station_indicators_table(station_indicators, db_connection)


def append_to_station_indicators_dict(station_indicators, station_name, column):
    """
    Appends station and indicator data to the `station_indicators` dictionary.

    This function appends a new entry to the `station_indicators` dictionary, adding the station's ID, 
    the indicator's ID, and a placeholder for the description based on the provided station name and column.

    Parameters:
        station_indicators (dict): A dictionary holding station indicator data with keys 'idStation', 
                                    'idIndicator', and 'description'. It is updated by this function.
        station_name (str): The name of the station.
        column (str): The name of the indicator column.

    Returns:
        dict: The updated `station_indicators` dictionary with the new station and indicator data appended.
    """
    station_indicators['idStation'].append(STATIONS[station_name][0])
    station_indicators['idIndicator'].append(INDICATORS[column.upper()])
    station_indicators['description'].append("")
    return station_indicators


def append_to_measure_indicator_table(df, station_name, column, db_connection):
    """
    Appends data from a DataFrame to the 'measure_indicator' table in the database.

    This function extracts the relevant columns from the provided DataFrame, processes the data by adding 
    station and indicator IDs, renames the value column, drops any rows with missing data, and then appends 
    the data to the 'measure_indicator' table in the specified database.

    Parameters:
        df (pandas.DataFrame): A DataFrame containing the indicator data with a 'datetime' column and 
                               a column for the indicator values.
        station_name (str): The name of the station.
        column (str): The name of the indicator column in the DataFrame.
        db_connection (SQLAlchemy Connection): A connection to the database where the data should be appended.

    Returns:
        bool: `True` if the data was successfully appended to the 'measure_indicator' table, 
              `False` if an error occurred during the operation.
    """
    df_indicator = df[['datetime', column]].copy()
    df_indicator['idStation'] = STATIONS[station_name][0]
    df_indicator['idIndicator'] = INDICATORS[column.upper()]
    df_indicator.rename(columns={column: 'value'}, inplace=True)
    df_indicator = df_indicator.dropna()
    try:
        df_indicator.to_sql('measure_indicator', con=db_connection, if_exists='append',
                            index=False, chunksize=1000)
        return True
    except:
        return False


def append_to_station_indicators_table(station_indicators, db_connection):
    """
    Appends station-indicator mapping data to the 'station_indicators' table in the database.

    This function converts the provided dictionary of station-indicator mappings into a pandas DataFrame 
    and appends the data to the 'station_indicators' table in the specified database connection. The data 
    includes mappings between station IDs and indicator IDs.

    Parameters:
        station_indicators (dict): A dictionary containing station-indicator mappings. The dictionary should
                                    include keys 'idStation', 'idIndicator', and 'description'.
        db_connection (SQLAlchemy Connection): A connection to the database where the data should be appended.

    Returns:
        None
    """
    station_indicators_df = pd.DataFrame(station_indicators)
    station_indicators_df.to_sql('station_indicators', con=db_connection, if_exists='append', index=False)


def adjust_time_string(datetime_str):
    """
    Adjusts '24:00' to '00:00' of the next day in datetime strings.

    This function takes a datetime string, checks if the time is '24:00', and if so, 
    adjusts the time to '00:00' of the following day. The date is incremented by one day 
    to reflect this adjustment, and the new datetime string is returned in the format 'YYYY/MM/DD 00:00'.
    
    Parameters:
        datetime_str (str): A string representing a datetime, typically in the format 'YYYY/MM/DD HH:MM'.
        
    Returns:
        str: The adjusted datetime string if '24:00' is found, otherwise returns the original input string.
    """
    if '24:00' in datetime_str:
        date_part = datetime_str.split(' ')[0]
        new_date = pd.to_datetime(date_part) + pd.DateOffset(days=1)
        return new_date.strftime('%Y/%m/%d') + ' 00:00'
    return datetime_str


if __name__ == "__main__":
    populate_tables()
