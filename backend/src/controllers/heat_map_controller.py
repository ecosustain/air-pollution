from repositories import (
    MeasureIndicatorRepository
)

from models import(
    MeasureIndicator
)

from datetime import datetime
import sys, os
import math
import numpy as np

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
            "KNN": KNNInterpolator,
            "Kriging": KrigingInterpolator,
        }

    def get_heat_map(
        self,
        payload: dict
    ) -> list[dict]:
        date_str = payload["datetime"]
        indicator = payload["indicator"]
        interpolator_dict = payload["interpolator"]

        interpolator_method = interpolator_dict["method"]
        parameter = interpolator_dict["params"]

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
    
    def __get_rectangular_discretization(self) -> list[tuple]:
        borders_coordinates = {
            "min_lat": -24.00736242788278,
            "max_lat": -23.35831688708724,
            "min_long": -46.83459631388834,
            "max_long": -46.36359807038185,
        }

        number_of_lat_points = 20 
        
        lat_range = np.linspace(borders_coordinates['min_lat'], borders_coordinates['max_lat'], number_of_lat_points)
        
        lat_distance = borders_coordinates['max_lat'] - borders_coordinates['min_lat']
        long_distance = borders_coordinates['max_long'] - borders_coordinates['min_long']
        
        aspect_ratio = lat_distance / long_distance
        number_of_long_points = int(number_of_lat_points / aspect_ratio)
        
        long_range = np.linspace(borders_coordinates['min_long'], borders_coordinates['max_long'], number_of_long_points)

        area_discretization = [(lat, lon) for lat in lat_range for lon in long_range]
        area_discretization = self.__remove_distant_points(area_discretization=area_discretization)

        return  area_discretization
    
    def __remove_distant_points(
        self,
        area_discretization: list[tuple]
    ) -> list[tuple]:
        new_area_discretization = []
        threshold = 7
        for point in area_discretization:
            min_dist = float("inf")
            for station_coordinates in STATIONS_ID.values():
                dist = self.__haversine_dist(point[0], point[1], station_coordinates[0], station_coordinates[1])
                if dist < min_dist:
                    min_dist = dist
            if min_dist < threshold:
                new_area_discretization.append(point)
        return new_area_discretization

    def __haversine_dist(self, lat1, lon1, lat2, lon2):
        R = 6371.0

        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c

        return distance

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




