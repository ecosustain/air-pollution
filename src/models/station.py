from sqlalchemy import Column, Integer, String, Numeric, Boolean

class Station():
    __tablename__ = "station"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    longitude = Column(Numeric)
    latitude = Column(Numeric)
    is_pollutant = Column(Boolean)