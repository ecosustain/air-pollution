from meta_data import stations
from sqlalchemy import (create_engine, Column, Integer, MetaData, Table, DateTime, Double,
                        text, String, Boolean, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd


# Database connection string
DATABASE_URL = "mysql+pymysql://root:root@localhost"

# Create an engine
engine = create_engine(DATABASE_URL)

# Create a connection
with engine.connect() as connection:
    # Execute SQL to create the schema
    connection.execute(text("CREATE DATABASE IF NOT EXISTS poluicao"))

# Create a base class
Base = declarative_base()

tables_and_columns = {
    "stations": [
        ("id", Integer, True),
        ("name", String(255), False),
        ("longitude", Double, False),
        ("latitude", Double, False),
        ("description", String(255), False),
    ],
    "indicators": [
        ("id", Integer, True),
        ("name", String(255), False),
        ("description", String(255), False),
        ("measure_unit", String(255), False),
        ("is_pollutant", Boolean, False),
    ],
    "station_indicators": [
        ("id", Integer, True),
        ("idStation", Integer, False, "stations.id"),
        ("idIndicator", Integer, False, "indicators.id"),
        ("description", String(255), False),
        ("period", DateTime, False)
    ]
}

for station in stations:
    cols = [
        ('id', Integer, True),  # (column_name, column_type, is_primary_key)
        ('datetime', DateTime, False)
    ]
    df = pd.read_csv(f"./stations_data/{station}.csv", nrows=1)
    df_cols = df.columns
    df_cols = df_cols[1:]

    for col in df_cols:
        cols.append((str(col), Double, False))

    tables_and_columns[station] = cols

print(tables_and_columns)

# Create tables dynamically with foreign key constraints
metadata = MetaData(schema='poluicao')

for table_name, columns in tables_and_columns.items():
    table_columns = []
    for column_name, column_type, is_primary_key, *fk in columns:
        if fk:
            # If the column has a foreign key, create a ForeignKey constraint
            column = Column(column_name, column_type, ForeignKey(fk[0]), primary_key=is_primary_key)
        else:
            column = Column(column_name, column_type, primary_key=is_primary_key)
        table_columns.append(column)

    # Define the table
    Table(table_name, metadata, *table_columns)

# Create all tables
metadata.create_all(engine)

print("Tables created successfully.")
