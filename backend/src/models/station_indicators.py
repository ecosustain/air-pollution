from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class StationIndicators(Base):
    __tablename__ = "station_indicators"
    station_id = Column(Integer, ForeignKey('stations.id'), primary_key=True)
    indicator_id = Column(Integer, ForeignKey('indicators.id'), primary_key=True)
    description = Column(String)

    station = relationship("Stations")
    indicator = relationship("Indicators")
