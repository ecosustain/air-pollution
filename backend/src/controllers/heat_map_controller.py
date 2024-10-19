from repositories import (
    MeasureIndicatorRepository
)

from datetime import datetime
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from metadata.meta_data import INDICATORS

class HeatMapController:
    def __init__(self, session) -> None:
        self.measure_indicator_repository = MeasureIndicatorRepository(session)
        self.session = session

    def get_heat_map(self, payload: dict) -> list[dict]:

        initial_date_str = payload["initial_date"]
        final_date_str = payload["final_date"]
        indicator = payload["indicator"]

        initial_date = datetime.strptime(initial_date_str, '%Y-%m-%d %H:%M:%S')
        final_date = datetime.strptime(final_date_str, '%Y-%m-%d %H:%M:%S')

        indicator_id = INDICATORS[indicator]

        measure_indicators = self.measure_indicator_repository.get_measure_indicators(initial_date=initial_date,
                                                                                      final_date=final_date,
                                                                                      indicator_id=indicator_id)

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



