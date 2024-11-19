from sqlalchemy import (create_engine, Column, Integer, MetaData, Table, DateTime, Double,
                        text, String, Boolean, ForeignKey, Index)
from backend.src.utils.credentials import LOGIN_MYSQL, PASSWORD_MYSQL


def create_tables():
    engine = create_database()
    tables_and_columns = define_tables_and_columns()
    metadata = MetaData(schema='poluicao')

    for table_name, columns in tables_and_columns.items():
        table_columns = []
        for column_name, column_type, is_primary_key, *fk in columns:
            column = create_column(column_name, column_type, is_primary_key, *fk)
            table_columns.append(column)
        create_table(table_name, metadata, *table_columns)

    metadata.create_all(engine)
    print("Tables and indexes created successfully.")


def create_database():
    DATABASE_URL = f"mysql+pymysql://{LOGIN_MYSQL}:{PASSWORD_MYSQL}@localhost"
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        connection.execute(text("CREATE DATABASE IF NOT EXISTS poluicao"))
    return engine


def define_tables_and_columns():
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
    return tables_and_columns


def create_column(column_name, column_type, is_primary_key, *fk):
    if fk:
        column = Column(column_name, column_type, ForeignKey(fk[0]), primary_key=is_primary_key)
    else:
        column = Column(column_name, column_type, primary_key=is_primary_key)
    return column


def create_table(table_name, metadata, *table_columns):
    table = Table(table_name, metadata, *table_columns)
    if table_name == 'measure_indicator':
        Index('idx_datetime', table.c.datetime) # B+ Tree index
        Index('idx_idStation_hash', table.c.idStation, mysql_using='hash') # Hash index
        Index('idx_idIndicator_hash', table.c.idIndicator, mysql_using='hash') # Hash index


if __name__ == "__main__":
    create_tables()
