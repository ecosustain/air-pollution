from sqlalchemy import (create_engine, Column, Integer, MetaData, Table, DateTime, Double,
                        text, String, Boolean, ForeignKey, Index)
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

# Define the table structures
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
        ("idStation", Integer, True, "stations.id"),
        ("idIndicator", Integer, True, "indicators.id"),
        ("description", String(255), False),
    ],
    "measure_indicator": [
        ("idStation", Integer, True, "stations.id"),
        ("idIndicator", Integer, True, "indicators.id"),
        ("datetime", DateTime, True),
        ("value", Double, False)
    ]
}

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
    table = Table(table_name, metadata, *table_columns)

    # If it's the "measure_indicator" table, add indexes
    
    if table_name == 'measure_indicator':
        # B+ Tree index (default) on datetime
        Index('idx_datetime', table.c.datetime)
        
        # Hash indexes on idStation and idIndicator
        Index('idx_idStation_hash', table.c.idStation, mysql_using='hash')
        Index('idx_idIndicator_hash', table.c.idIndicator, mysql_using='hash')

# Create all tables
metadata.create_all(engine)

print("Tables and indexes created successfully.")
