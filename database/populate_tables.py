import os
import pandas as pd
from sqlalchemy import create_engine

# MySQL connection setup
db_connection = create_engine('mysql+mysqlconnector://root:root@localhost/poluicao')

# Directory containing the CSV files
csv_dir = '../scrapper/scrapped_data'

# Function to determine table name (assuming CSV name matches table name, adjust if necessary)
def get_table_name(file_name):
    table_name = file_name.split('.')[0]  # Removes '.csv' from the filename
    return table_name

# Loop through all CSV files in the directory
for file_name in os.listdir(csv_dir):
    if file_name.endswith('.csv'):  # Process only CSV files
        file_path = os.path.join(csv_dir, file_name)
        
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Get the corresponding table name
        table_name = get_table_name(file_name)
        
        # Store the data into the MySQL table
        df.to_sql(table_name, con=db_connection, if_exists='append', index=False)
        print(f"Data from {file_name} has been inserted into {table_name}")

print("All files processed successfully.")
