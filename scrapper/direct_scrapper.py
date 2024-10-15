'''
TO-DO:
- Refactor scripts (create file for update).
'''

import requests
from credentials import login_qualar, password_qualar, login_mysql, password_mysql
import os, sys
import pandas as pd
from datetime import datetime, timedelta
import tempfile
from sqlalchemy import create_engine, text
from utils import ddmmyyyyhhmm_yyyymmddhhmm, string_to_float
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from metadata.meta_data import stations, indicators

def login_qualar():
    url = 'https://qualar.cetesb.sp.gov.br/qualar/autenticador'
    payload = {
        'cetesb_login': login_qualar,
        'cetesb_password': password_qualar,
        'enviar': 'OK'
    }
    response = requests.post(url, data=payload)
    return response.cookies

def get_session_id():
    cookies = login_qualar()
    session_id = None
    for cookie in cookies:
        session_id = cookie.value
    return session_id

def check_valid_dates(start_date, end_date):
    try:
        start_date_obj = datetime.strptime(start_date, "%d/%m/%Y")
        end_date_obj = datetime.strptime(end_date, "%d/%m/%Y")
        return end_date_obj > start_date_obj
    except ValueError:
        return False

def get_request_response(session_id, start_date, end_date, station, indicator):
    if not check_valid_dates(start_date, end_date):
        return None
    url = "https://qualar.cetesb.sp.gov.br/qualar/exportaDadosAvanc.do?method=exportar"
    headers = {'Cookie': f"JSESSIONID={session_id}"}
    payload = { 'dataInicialStr': start_date,
                'dataFinalStr': end_date,
                'estacaoVO.nestcaMonto': station,
                'nparmtsSelecionados': indicator    }
    
    response = requests.post(url, headers=headers, data=payload)
    if ("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\">" in response.text):
        return None
    return response.text

def get_data(session_id, interval_years=(2000, 2024), interval_size=1):
    for station in stations:
        for indicator in indicators:
            for year in range(interval_years[1], interval_years[0], -interval_size):
                start_date = f"01/01/{year - interval_size}"
                end_date = f"01/01/{year}"
                response_text = get_request_response(session_id, start_date, end_date,
                                                     stations[station][0], indicators[indicator])
                if response_text is not None:
                    save_csv_file(response_text, station, indicator, str(year - interval_size), str(year))
                    print(f"Succesfully saved: {station} - {indicator} - {year - interval_size}:{year}")

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

def update_data(session_id, data_directory="./data/scraped_data"):
    for file in os.listdir(data_directory):
        dfs_to_update_csv = {}
        df = get_df_from_csv(data_directory, file)
        if df is None:
            continue
        start_date, end_date = get_dates_to_update(df)
        station = file[:-4]
        for indicator in indicators:
            response_text = get_request_response(session_id, start_date, end_date,
                                                     stations[station][0], indicators[indicator])
            if response_text is not None:
                df_to_update_csv = update_database(response_text, station, indicator)
                print(f"Successful database update: {station} - {indicator} - up to {end_date}")
                dfs_to_update_csv[indicator.lower()] = df_to_update_csv
        update_csv_file(df, dfs_to_update_csv, data_directory, file)
        
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

def fix_time_format(date_str):
    if "24:00" in date_str:
        date_str = date_str.replace("24:00", "00:00")
        return pd.to_datetime(date_str) + pd.Timedelta(days=1)
    else:
        return pd.to_datetime(date_str)

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

def adjust_columns_and_data(df, station, indicator):
    df.columns = ["date", "time", "value"]
    df = adjust_datetime_column(df)
    df["value"] = df["value"].map(string_to_float)
    df['idStation'] = stations[station][0]
    df['idIndicator'] = indicators[indicator]
    df.drop_duplicates(inplace=True)
    df = df[df['value'].notnull()]
    df['value'] = df['value'].astype(float)

    df_to_update_csv = df[['datetime', 'value']].copy() # will be used for updating the csv file
    df_to_update_csv.rename(columns={'value': indicator.lower()}, inplace=True)
    return df.dropna(), df_to_update_csv.dropna()

def update_database(data, station, indicator):
    db_url = f"mysql+pymysql://{login_mysql}:{password_mysql}@localhost/poluicao"
    db_connection = create_engine(db_url)
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "temp_file.csv")
        with open(file_path, "w") as file:
            file.write(data)
            df_to_update_csv = update_measure_indicator_table(file_path, station, indicator,
                                                              db_connection)
            update_station_indicators_table(station, indicator, db_connection)
    return df_to_update_csv
            
def update_measure_indicator_table(file_path, station, indicator, db_connection):
    df = pd.read_csv(file_path, sep=";", skiprows=7, encoding="latin1").dropna()
    df, df_to_update_csv = adjust_columns_and_data(df, station, indicator)
    df.to_sql('measure_indicator', con=db_connection, if_exists='append',
                index=False, chunksize=1000)
    return df_to_update_csv

def update_station_indicators_table(station, indicator, db_connection):
    id_station = stations[station][0]
    id_indicator = indicators[indicator]
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


def save_csv_file(data, station_name, indicator_name, start_year, end_year):
    directory = "./data/scraped_data"
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = f"{directory}/{station_name}_{indicator_name}_{start_year}_{end_year}.csv"
    with open(file_path, "w") as fp:
        fp.write(data)

if __name__ == "__main__":
    #get_data(get_session_id(), interval_size=8)
    update_data(get_session_id())