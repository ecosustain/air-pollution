from sqlalchemy import Column, Integer, String, Numeric

class Indicator():
    __tablename__ = "indicator"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    measure_unit = Column(Numeric)
    latitude = Column(Numeric)