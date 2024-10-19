import os, sys
import pandas as pd
from sqlalchemy import create_engine

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from backend.data.utils.credentials import LOGIN_MYSQL, PASSWORD_MYSQL
from metadata.meta_data import stations, indicators

def populate_tables():
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
    stations_data = {
        "id": [stations[station][0] for station in stations],
        "name": [station for station in stations],
        "latitude": [stations[station][1] for station in stations],
        "longitude": [stations[station][2] for station in stations],
        "description": ["" for _ in stations]  # Placeholder for description
    }
    stations_df = pd.DataFrame(stations_data)
    stations_df.to_sql('stations', con=db_connection, if_exists='append', index=False)

def insert_indicators_data(db_connection):
    indicator_data = {
        "id": [indicators[indicator] for indicator in indicators],
        "name": [indicator.lower() for indicator in indicators],
        "description": ["" for _ in indicators],  # Placeholder for description
        "measure_unit": ["" for _ in indicators],  # Placeholder for measure unit
        "is_pollutant": [True for _ in indicators]  # Assume all are pollutants
    }
    indicators_df = pd.DataFrame(indicator_data)
    indicators_df.to_sql('indicators', con=db_connection, if_exists='append', index=False)

def insert_data_from_station(file_path, station_name, db_connection):
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
    station_indicators['idStation'].append(stations[station_name][0])
    station_indicators['idIndicator'].append(indicators[column.upper()])
    station_indicators['description'].append("")
    return station_indicators

def append_to_measure_indicator_table(df, station_name, column, db_connection):
    df_indicator = df[['datetime', column]].copy()
    df_indicator['idStation'] = stations[station_name][0]
    df_indicator['idIndicator'] = indicators[column.upper()]
    df_indicator.rename(columns={column: 'value'}, inplace=True)
    df_indicator = df_indicator.dropna()
    try:
        df_indicator.to_sql('measure_indicator', con=db_connection, if_exists='append',
                            index=False, chunksize=1000)
        return True
    except:
        return False

def append_to_station_indicators_table(station_indicators, db_connection):
    station_indicators_df = pd.DataFrame(station_indicators)
    station_indicators_df.to_sql('station_indicators', con=db_connection, if_exists='append', index=False)

def adjust_time_string(datetime_str):
    """Adjust '24:00' to '00:00' of the next day in datetime strings."""
    if '24:00' in datetime_str:
        date_part = datetime_str.split(' ')[0]
        new_date = pd.to_datetime(date_part) + pd.DateOffset(days=1)
        return new_date.strftime('%Y/%m/%d') + ' 00:00'
    return datetime_str

if __name__ == "__main__":
    populate_tables()