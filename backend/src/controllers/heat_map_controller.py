from repositories import (
    MeasureIndicatorRepository
)

from models import(
    MeasureIndicator
)

from datetime import datetime
import sys, os
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from metadata.meta_data import INDICATORS, STATIONS_ID
from backend.interpolation.interpolator import (
    KNNInterpolator,
    KrigingInterpolator,
)

class HeatMapController:
    def __init__(self, session) -> None:
        self.measure_indicator_repository = MeasureIndicatorRepository(session)
        self.session = session
        self.interpolators = {
            "KNNInterpolator": KNNInterpolator,
            "KrigingInterpolator": KrigingInterpolator,
        }

    def get_heat_map(
        self,
        payload: dict
    ) -> list[dict]:
        date_str = payload["datetime"]
        indicator = payload["indicator"]
        interpolator_dict = payload["interpolator"]

        interpolator_method = interpolator_dict["method"]
        parameter = interpolator_dict["parameter"]

        date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

        indicator_id = INDICATORS[indicator]

        area_discretization = self.__get_rectangular_discretization()

        measure_indicators = self.measure_indicator_repository.get_measure_indicators(date=date,
                                                                                      indicator_id=indicator_id)
        
        interpolator_input = self.__build_interpolator_input(area_discretization=area_discretization,
                                                             measure_indicators=measure_indicators)


        interpolator = self.interpolators[interpolator_method](interpolator_input, parameter)

        y = interpolator.predict(X=area_discretization)

        response = [{"lat": coordinates[0], "long": coordinates[1], "value": value} for coordinates, value in zip(area_discretization,y)]
        
        return response
    
    top = [-23.5737757 + 0.4, -46.7369984 - 0.2]
    bottom = [-23.5737757 - 0.4, -46.7369984 + 0.6]
    
    def __get_rectangular_discretization(
        self
    ) -> list[tuple]:
        borders_coordinates = {
            "min_lat": -23.5737757 - 0.4,
            "max_lat": -23.5737757 + 0.4,
            "min_long": -46.7369984 - 0.2,
            "max_long": -46.7369984 + 0.6,
        }

        step_size = 0.005

        lat_range = list(self.__get_range(borders_coordinates["min_lat"], borders_coordinates["max_lat"], step_size))
        long_range = list(self.__get_range(borders_coordinates["min_long"], borders_coordinates["max_long"], step_size))

        matrix_of_tuples = [(lat, lon) for lat in lat_range for lon in long_range]

        return matrix_of_tuples

    def __get_range(
        self,
        start: float,
        stop: float,
        step: float,
    ):
        while start <= stop:
            yield round(start, 6)
            start += step

    def __build_interpolator_input(
        self,
        area_discretization: list[list],
        measure_indicators: list[MeasureIndicator]
    ) -> dict[tuple,float]:
        y = []
        for _ in area_discretization:
            y.append(math.nan)
        
        y = self.__fill_known_points(area_discretization=area_discretization,
                          y=y,
                          measure_indicators=measure_indicators)
        
        interpolator_input = {tuple(a):b for a,b in zip(area_discretization,y)}

        return interpolator_input

    def __fill_known_points(
        self,
        area_discretization: list,
        y: list,
        measure_indicators: list[MeasureIndicator]
    ) -> list:
        for measure_indicator in measure_indicators:
            station_coordinates = STATIONS_ID[measure_indicator.idStation]
            min_dist_index = self.__get_closer_point(area_discretization=area_discretization,
                                            station_coordinates=station_coordinates)
            y[min_dist_index] = measure_indicator.value
        
        return y

    def __get_closer_point(
        self,
        area_discretization: list[tuple],
        station_coordinates: tuple
    ) -> int:
        min_dist = float("inf")
        min_dist_index = None

        for i in range(len(area_discretization)):
            point = area_discretization[i]
            dist = math.sqrt((point[0] - station_coordinates[0]) ** 2 + (point[1] - station_coordinates[1]) ** 2)
            if dist < min_dist:
                min_dist_index = i
                min_dist = dist
        
        return min_dist_index




