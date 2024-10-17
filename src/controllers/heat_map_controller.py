from repositories import (
    MeasureIndicatorRepository
)

from datetime import datetime

class HeatMapController:
    def __init__(self, session) -> None:
        self.measure_indicator_repository = MeasureIndicatorRepository(session)
        self.session = session

    def get_heat_map(self, payload: dict) -> list[dict]:

        initial_date_str = payload["initial_date"]
        final_date_str = payload["final_date"]

        initial_date = datetime.strptime(initial_date_str, '%Y-%m-%d %H:%M:%S')
        final_date = datetime.strptime(final_date_str, '%Y-%m-%d %H:%M:%S')

        measure_indicators = self.measure_indicator_repository.get_measure_indicators(initial_date=initial_date,
                                                                                      final_date=final_date,
                                                                                      limit=5)

        # construir a entrada para o interpolador () -> list[ [latitude, longitude] ]


        # chamar o interpolador


        # retornar lista de dicts {"latitude": , "longitude":, "valor": }

        for measure_indicator in measure_indicators:
            print(measure_indicator.datetime)
            print(measure_indicator.idIndicator)
            print(measure_indicator.idStation)
            print(measure_indicator.value)
            print()

        return measure_indicators



