from models import MeasureIndicator

import datetime

class MeasureIndicatorRepository:
    def __init__(self, session) -> None:
        self.session = session

    def get_measure_indicators(
        self,
        initial_date: datetime,
        final_date: datetime,
        limit: int
    ) -> list[MeasureIndicator]:
        
        measure_indicators = (self.session.query(MeasureIndicator)
                              .filter(MeasureIndicator.datetime >= initial_date)
                              .filter(MeasureIndicator.datetime <= final_date)
                              .limit(limit)
                              .all()
                              )
        
        return measure_indicators