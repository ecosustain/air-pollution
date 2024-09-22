import os, sys
import pandas as pd
from sqlalchemy import create_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from metadata.meta_data import stations, indicators

# MySQL connection setup (change username and password)
db_connection = create_engine('mysql+pymysql://root:root@localhost/poluicao')

# Directory containing the CSV files
csv_dir = './scrapper/scrapped_data'

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

# Loop through all CSV files in the directory
for file_name in os.listdir(csv_dir):
    if file_name.endswith('.csv'):  # Process only CSV files
        file_path = os.path.join(csv_dir, file_name)
        
        # Read the CSV file
        df = pd.read_csv(file_path)
        df['datetime'] = df['datetime'].apply(adjust_time)
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y/%m/%d %H:%M')
        
        # Get the corresponding table name
        table_name = get_table_name(file_name)
        
        # Store the data into the MySQL table
        df.to_sql(table_name, con=db_connection, if_exists='append', index=False)
        print(f"Data from {file_name} has been inserted into {table_name}")

print("All files processed successfully.")
