from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Stations(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    longitude = Column(Numeric)
    latitude = Column(Numeric)
    description = Column(String)
