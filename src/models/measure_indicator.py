from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from models import Stations, Indicators

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class MeasureIndicators(Base):
    __tablename__ = "measure_indicators"

    id = Column(Integer, primary_key=True)
    station_id = Column(ForeignKey(Stations.id))
    indicator_id = Column(ForeignKey(Indicators.id))
    datetime = Column(DateTime)
    value = Column(Float)

    station = relationship("Stations")
    indicator = relationship("Indicators")
