from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Indicators(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    measure_unit = Column(Numeric)
