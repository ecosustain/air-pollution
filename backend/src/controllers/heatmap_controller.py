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
        self.TIME_REFERENCE_MAP = {
            "instant": {
                "isPeriod": False,
                "payload_field": "hour",
                "heatmaps_keys": range(1,2),
            },
            "hourly": {
                "isPeriod": False,
                "payload_field": "day",
                "heatmaps_keys": range(0,24),
            },
            "daily": {
                "isPeriod": False,
                "payload_field": "month",
                "heatmaps_keys": range(1,31),
            },
            "monthly": {
                "isPeriod": False,
                "payload_field": "year",
                "heatmaps_keys": range(1,13),
            },
            "yearly": {
                "isPeriod": True,
                "first_time_reference": "first_year",
                "last_time_reference": "last_year",
            },
        }

    def get_heatmap(
        self,
        payload: dict
    ) -> list[dict]:
        indicator = payload["indicator"]
        interpolator_dict = payload["interpolator"]
        indicator_id = INDICATORS[indicator]

        interpolator_method = interpolator_dict["method"]
        parameters = interpolator_dict["params"]

        interval = payload["interval"]
        interval_map = self.TIME_REFERENCE_MAP[interval]

        if interval_map["isPeriod"]:
            first_time_reference_str = payload[interval_map["first_time_reference"]]
            last_time_reference_str = payload[interval_map["last_time_reference"]]

            heatmaps_keys = range(int(first_time_reference_str), int(last_time_reference_str) + 1)

            time_reference_str = None
        else:
            payload_field = interval_map["payload_field"]
            time_reference_str = payload[payload_field]

            heatmaps_keys = interval_map["heatmaps_keys"]

        area_discretization = self.__get_rectangular_discretization()
        
        response = self.__get_heatmaps(heatmaps_keys=heatmaps_keys,
                                       time_reference_str=time_reference_str,
                                       indicator_id=indicator_id,
                                       area_discretization=area_discretization,
                                       interpolator_method=interpolator_method,
                                       parameters=parameters,)
         
        return response
    
    top = [-23.5737757 + 0.4, -46.7369984 - 0.2]
    bottom = [-23.5737757 - 0.4, -46.7369984 + 0.6]

    def __get_heatmaps(
        self,
        heatmaps_keys: list,
        time_reference_str: str,
        indicator_id: int,
        area_discretization,
        interpolator_method: str,
        parameters,
    ):
        response = {}
        for key in heatmaps_keys:
            incremented_time_reference_str = self.__increment_time_reference_str(time_reference_str, key)

            mean_values = self.measure_indicator_repository.get_mean_measure_indicators(time_reference_str=incremented_time_reference_str,
                                                                                            indicator_id=indicator_id)
            if len(mean_values) > 0:
                interpolator_input = self.__build_interpolator_input(area_discretization=area_discretization,
                                                                    measure_indicators=mean_values)
                
                interpolator = self.interpolators[interpolator_method](interpolator_input, parameters)

                y = interpolator.predict(X=area_discretization)

                heat_map = [{"lat": coordinates[0], "long": coordinates[1], "value": value} for coordinates, value in zip(area_discretization,y)]
            else:
                heat_map = {}

            key = str(key)
            response[key] = heat_map
        
        return response
    
    def __increment_time_reference_str(self, time_reference_str, key):
        str_key = str(key)
        if len(str_key) == 1:
            str_key = "0" + str_key

        if time_reference_str is None:
            return str_key

        datetime_list = time_reference_str.split(" ")

        date_list = datetime_list[0].split("-")
        if len(date_list) < 3:
            return time_reference_str + "-" + str_key
        if len(date_list) == 3:
            return time_reference_str + " " + str_key

    
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




