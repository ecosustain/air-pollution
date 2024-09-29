from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from models import Station, Indicator

class StationIndicator():
    __tablename__ = "station_indicators"
    id = Column(Integer, primary_key=True)
    station_id = Column(ForeignKey(Station.id))
    indicator_id = Column(ForeignKey(Indicator.id))
    description = Column(String)

    station = relationship("Station")
    indicator = relationship("Indicator")
