from sqlalchemy import (create_engine, Column, Integer, MetaData, Table, DateTime, Double,
                        text, String, Boolean, ForeignKey, Index)
from utils.db_utils import with_session


@with_session
def create_tables(session):
    """
    Creates all tables and indexes defined in the `tables_and_columns` dictionary 
    within the 'poluicao' schema in the MySQL database.

    Workflow:
    - Initializes the database connection.
    - Defines the tables and columns through the `define_tables_and_columns()` method.
    - Creates each table along with its columns and any necessary foreign key constraints.
    - Adds specific indexes to the 'measure_indicator' table for optimization.
    - Calls `metadata.create_all(engine)` to create the tables in the database.

    Returns:
        None
    """
    engine = create_database(session)
    tables_and_columns = define_tables_and_columns()
    metadata = MetaData(schema='poluicao')

    for table_name, columns in tables_and_columns.items():
        table_columns = []
        for column_name, column_type, is_primary_key, *fk in columns:
            column = create_column(column_name, column_type, is_primary_key, *fk)
            table_columns.append(column)
        create_table(table_name, metadata, *table_columns)

    metadata.create_all(bind=engine)
    print("Tables and indexes created successfully.")


def create_database(session):
    """
    Creates the 'poluicao' database if it doesn't already exist. Uses the session 
    for the operation to ensure that the same connection is used for database creation.

    Parameters:
        session (SQLAlchemy Session): The active session used for database operations.

    Returns:
        engine: The SQLAlchemy engine connected to the database.
    """
    engine = session.get_bind()
    with engine.connect() as connection:
        connection.execute(text("CREATE DATABASE IF NOT EXISTS poluicao"))
    return engine


def define_tables_and_columns():
    """
    Defines the schema for the database tables and their respective columns, including their 
    data types and whether they are primary keys or foreign keys.

    Returns:
        dict: A dictionary mapping table names to lists of columns and their properties.
    """
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
    """
    Creates a column for a table, including handling primary key and foreign key constraints.

    Parameters:
        column_name (str): The name of the column.
        column_type (SQLAlchemy type): The SQLAlchemy data type of the column.
        is_primary_key (bool): Whether this column is a primary key.
        *fk (tuple): Optional; foreign key relationship, specifying the referenced column (e.g., 
                     "table_name.column_name").

    Returns:
        sqlalchemy.Column: The SQLAlchemy `Column` object representing the column in the table.
    """
    if fk:
        column = Column(column_name, column_type, ForeignKey(fk[0]), primary_key=is_primary_key)
    else:
        column = Column(column_name, column_type, primary_key=is_primary_key)
    return column


def create_table(table_name, metadata, *table_columns):
    """
    Creates a table using SQLAlchemy, including its columns and associated indexes.

    Parameters:
        table_name (str): The name of the table to create.
        metadata (sqlalchemy.MetaData): The metadata object that holds the table definition.
        *table_columns (sqlalchemy.Column): A variable number of `sqlalchemy.Column` objects 
                                             representing the columns in the table.

    Returns:
        None

    Notes:
        - For the `measure_indicator` table, additional indexes are created on the `datetime`, 
          `idStation`, and `idIndicator` columns to optimize queries involving these fields.
    """
    table = Table(table_name, metadata, *table_columns)
    if table_name == 'measure_indicator':
        Index('idx_datetime', table.c.datetime) # B+ Tree index
        Index('idx_idStation_hash', table.c.idStation, mysql_using='hash') # Hash index
        Index('idx_idIndicator_hash', table.c.idIndicator, mysql_using='hash') # Hash index


if __name__ == "__main__":
    create_tables()
