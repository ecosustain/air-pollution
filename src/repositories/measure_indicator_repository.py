from models import MeasureIndicators

class MeasureIndicatorRepository:
    def __init__(self, session) -> None:
        self.session = session

    def get_measure_indicators(self, limit: int) -> list[MeasureIndicators]:
        measure_indicators = (self.session.query(MeasureIndicators)
                              .limit(limit)
                              .all()
                              )
        
        return measure_indicators