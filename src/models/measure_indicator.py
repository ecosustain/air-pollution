from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey, Double, DateTime
from models import Station, Indicator

class MeasureIndicator():
    __tablename__ = "measure_indicator"

    id = Column(Integer, primary_key=True)
    station_id = Column(ForeignKey(Station.id))
    indicator_id = Column(ForeignKey(Indicator.id))
    datetime = Column(DateTime)
    value = Column(Double)

    station = relationship("Station")
    indicator = relationship("Indicator")
