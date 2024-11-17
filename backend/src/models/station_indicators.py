from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from models import Stations, Indicators

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class StationIndicators(Base):
    __tablename__ = "station_indicators"
    id = Column(Integer, primary_key=True)
    station_id = Column(ForeignKey(Stations.id))
    indicator_id = Column(ForeignKey(Indicators.id))
    description = Column(String)

    station = relationship("Stations")
    indicator = relationship("Indicators")
