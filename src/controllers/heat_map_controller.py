from repositories import (
    MeasureIndicatorRepository
)

import datetime

class HeatMapController:
    def __init__(self, session) -> None:
        self.measure_indicator_repository = MeasureIndicatorRepository(session)
        self.session = session

    def get_heat_map(self, date: datetime) -> list[dict]:

        # datetime_data = self.heat_map_repository.get_data(date)

        # construir a entrada para o interpolador () -> list[ [latitude, longitude] ]


        # chamar o interpolador


        # retornar lista de dicts {"latitude": , "longitude":, "valor": }

        measure_indicators = self.measure_indicator_repository.get_measure_indicators(limit=5)

        return measure_indicators



