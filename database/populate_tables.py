import os, sys
import pandas as pd
from sqlalchemy import create_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from metadata.meta_data import stations, indicators
from scrapper.credentials import login_mysql, password_mysql

# Database connection string
DATABASE_URL = f"mysql+pymysql://{login_mysql}:{password_mysql}@localhost/poluicao"

# MySQL connection setup (change username and password)
db_connection = create_engine(DATABASE_URL)

# Directory containing the CSV files
csv_dir = './data/scraped_data'

# Function to determine table name (assuming CSV name matches table name, adjust if necessary)
def get_table_name(file_name):
    table_name = file_name.replace(".csv", "")
    return table_name

def adjust_time(dt_str):
    if '24:00' in dt_str:
        date_part = dt_str.split(' ')[0]
        new_date = pd.to_datetime(date_part) + pd.DateOffset(days=1)
        return new_date.strftime('%Y/%m/%d') + ' 00:00'
    return dt_str

dict_aux = {
    "id": [],
    "name": [],
    "longitude": [],
    "latitude": [],
    "description": [],
}

for station in stations:
    dict_aux["id"].append(stations[station][0])
    dict_aux["name"].append(station)
    dict_aux["latitude"].append(stations[station][1])
    dict_aux["longitude"].append(stations[station][2])
    dict_aux["description"].append("")

stations_df = pd.DataFrame(dict_aux)
stations_df.to_sql('stations', con=db_connection, if_exists='append', index=False)    

dict_aux = {
    "id": [],
    "name": [],
    "description": [],
    "measure_unit": [],
    "is_pollutant": [],
}

for indicator in indicators:
    dict_aux["id"].append(indicators[indicator])
    dict_aux["name"].append(str(indicator).lower())
    dict_aux["description"].append("")
    dict_aux["measure_unit"].append("")
    dict_aux["is_pollutant"].append(True)

indicators_df = pd.DataFrame(dict_aux)
indicators_df.to_sql('indicators', con=db_connection, if_exists='append', index=False)  

#station_indicators_df = pd.DataFrame(dict_aux) 
# Loop through all CSV files in the directory
for file_name in os.listdir(csv_dir):
    if file_name.endswith('.csv'):  # Process only CSV files
        file_path = os.path.join(csv_dir, file_name)
        
        # Read the CSV file
        df = pd.read_csv(file_path)
        df['datetime'] = df['datetime'].apply(adjust_time)
        df['datetime'] = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%d %H:%M')
        
        dict_station_indicators = {
            "idStation": [],
            "idIndicator": [],
            "description": [],
        }

        # Get the corresponding table name
        table_name = get_table_name(file_name)
        for col in df.columns:
            if col != 'datetime':
                dict_station_indicators['description'].append("")
                dict_station_indicators['idStation'].append(stations[table_name][0])
                dict_station_indicators['idIndicator'].append(indicators[str(col).upper()])


                df_aux = df[['datetime', col]].copy()
                df_aux['idStation'] = stations[table_name][0]
                df_aux['idIndicator'] = indicators[str(col).upper()]
                df_aux.rename(columns={col : 'value'}, inplace=True)
                df_aux = df_aux.dropna()
                df_aux.to_sql('measure_indicator', con=db_connection, if_exists='append', index=False, chunksize=1000)

        # Store the data into the MySQL table
        station_indicators_df = pd.DataFrame(dict_station_indicators)
        #print(station_indicators_df)
        station_indicators_df.to_sql('station_indicators', con=db_connection, if_exists='append', index=False)
        
        print(f"Data from {file_name} has been inserted into measure_indicator")

print("All files processed successfully.")
