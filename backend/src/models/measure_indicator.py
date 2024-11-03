from sqlalchemy import Column, ForeignKey, Float, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class MeasureIndicator(Base):
    __tablename__ = "measure_indicator"

    idStation = Column(Integer, ForeignKey('stations.id'), primary_key=True)
    idIndicator = Column(Integer, ForeignKey('indicators.id'), primary_key=True)
    datetime = Column(DateTime, primary_key=True)
    value = Column(Float)
