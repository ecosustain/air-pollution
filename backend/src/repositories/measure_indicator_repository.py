from models import MeasureIndicator

import datetime

class MeasureIndicatorRepository:
    def __init__(self, session) -> None:
        self.session = session

    def get_measure_indicators(
        self,
        date: datetime,
        indicator_id: int
    ) -> list[MeasureIndicator]:
        
        measure_indicators = (self.session.query(MeasureIndicator)
                              .filter(MeasureIndicator.datetime == date)
                              .filter(MeasureIndicator.idIndicator == indicator_id)
                              .all()
                              )
        
        return measure_indicators