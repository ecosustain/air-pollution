from models import MeasureIndicator

class MeasureIndicatorRepository:
    def __init__(self, session) -> None:
        self.session = session

    def get_measure_indicators(self, limit: int) -> list[MeasureIndicator]:
        measure_indicators = (self.session.query(MeasureIndicator)
                              .limit(limit)
                              .all()
                              )
        
        return measure_indicators