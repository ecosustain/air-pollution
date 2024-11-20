from repositories import MeasureIndicatorRepository
from models import MeasureIndicator
import math
import numpy as np
from metadata.meta_data import INDICATORS, STATIONS_ID, RADIUS
from services.interpolation_service import KNNInterpolator, KrigingInterpolator


class HeatMapController:
    """
    Controller to manage the generation of heatmaps based on indicators data and interpolation methods.
    """

    def __init__(self, session) -> None:
        """
        Initialize the HeatMapController with a database session and set up repositories, interpolators, and mappings.
        
        Args:
            session: The database session used to query data.
        """

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
        self.MONTHS_HEATMAPS_KEYS = {
            "01": 31, "02": 29, "03": 31, "04": 30, "05": 31, "06": 30, "07": 31, "08": 31, "09": 30, "10": 31, "11": 30, "12": 31
        }

    def get_heatmap(
        self,
        payload: dict
    ) -> dict[dict]:
        """
        Generate heatmaps for a specified indicator, interval, and interpolator method.
        
        Args:
            payload (dict): A dictionary containing:
                - "indicator": The name of the indicator.
                - "interpolator": A dictionary with "method" (interpolation type) and "params" (parameters for the method).
                - "interval": The time interval for the heatmap (e.g., "daily", "monthly").
                - Additional time references based on the interval.

        Returns:
            dict[dict]: A dict of dictionaries representing the heatmap data for each time period.
        """

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

            if payload_field == "month":
                month = time_reference_str.split("-")[1]
                heatmaps_keys = range(1, self.MONTHS_HEATMAPS_KEYS[month] + 1)
            else:
                heatmaps_keys = interval_map["heatmaps_keys"]
        
        response = self.__get_heatmaps(heatmaps_keys=heatmaps_keys,
                                       time_reference_str=time_reference_str,
                                       indicator_id=indicator_id,
                                       interpolator_method=interpolator_method,
                                       parameters=parameters,
                                       indicator=indicator)
         
        return response
    
    top = [-23.5737757 + 0.4, -46.7369984 - 0.2]
    bottom = [-23.5737757 - 0.4, -46.7369984 + 0.6]

    def __get_heatmaps(
        self,
        heatmaps_keys: list,
        time_reference_str: str,
        indicator_id: int,
        interpolator_method: str,
        parameters,
        indicator: str,
    ):
        """
        Generate heatmaps for each time key in the interval.

        Args:
            heatmaps_keys (list): Keys representing specific time periods within the interval.
            time_reference_str (str): The base time reference string for the interval.
            indicator_id (int): The ID of the indicator.
            interpolator_method (str): The interpolation method to use.
            parameters: Parameters for the interpolation method.
            indicator (str): The name of the indicator.

        Returns:
            dict: A dictionary mapping time keys to heatmap data.
        """
        response = {}
        for key in heatmaps_keys:
            incremented_time_reference_str = self.__increment_time_reference_str(time_reference_str, key)

            mean_values = self.measure_indicator_repository.get_mean_measure_indicators(time_reference_str=incremented_time_reference_str,
                                                                                            indicator_id=indicator_id)
            if len(mean_values) > 0:
                area_discretization = self.__get_rectangular_discretization(mean_values, indicator)

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
        """
        Increment the time reference string by the given key.

        Args:
            time_reference_str (str): The base time reference string.
            key: The increment value.

        Returns:
            str: The updated time reference string.
        """
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

    
    def __get_rectangular_discretization(self, mean_values: list, indicator: str) -> list[tuple]:
        """
        Create a rectangular grid of coordinates within a specified area.

        Args:
            mean_values (list): List of mean values from the database.
            indicator (str): The name of the indicator.

        Returns:
            list[tuple]: A list of tuples representing the discretized area.
        """

        borders_coordinates = {
            "min_lat": -24.00736242788278,
            "max_lat": -23.35831688708724,
            "min_long": -46.83459631388834,
            "max_long": -46.36359807038185,
        }

        number_of_lat_points = 60  # Number of divisions in latitude
        
        lat_range = np.linspace(borders_coordinates['min_lat'], borders_coordinates['max_lat'], number_of_lat_points)
        
        lat_distance = borders_coordinates['max_lat'] - borders_coordinates['min_lat']
        long_distance = borders_coordinates['max_long'] - borders_coordinates['min_long']
        
        aspect_ratio = lat_distance / long_distance
        number_of_long_points = int(number_of_lat_points / aspect_ratio)
        
        long_range = np.linspace(borders_coordinates['min_long'], borders_coordinates['max_long'], number_of_long_points)

        area_discretization = [(lat, lon) for lat in lat_range for lon in long_range]
        area_discretization = self.__remove_distant_points(area_discretization=area_discretization,
                                                           mean_values=mean_values,
                                                           indicator=indicator)

        return  area_discretization
    
    def __remove_distant_points(
        self,
        mean_values,
        indicator,
        area_discretization: list[tuple]
    ) -> list[tuple]:
        """
        Remove points from the discretized area that are farther than a specified radius from any useful station.

        Args:
            mean_values (list): List of indicator measures.
            indicator (str): The indicator.
            area_discretization (list[tuple]): The list of discretized coordinates.

        Returns:
            list[tuple]: A filtered list of coordinates.
        """

        new_area_discretization = []

        for point in area_discretization:
            for measure_indicator in mean_values:
                if math.isnan(measure_indicator.value): continue

                station_coordinates = STATIONS_ID[measure_indicator.idStation]
                dist = self.__haversine_dist(point[0], point[1], station_coordinates[0], station_coordinates[1])

                if dist < RADIUS[indicator][measure_indicator.idStation]:
                    new_area_discretization.append(point)
                    break

        return new_area_discretization

    def __haversine_dist(self, lat1, lon1, lat2, lon2):
        """
        Calculate the Haversine distance between two geographic coordinates.

        Args:
            lat1 (float): Latitude of the first point.
            lon1 (float): Longitude of the first point.
            lat2 (float): Latitude of the second point.
            lon2 (float): Longitude of the second point.

        Returns:
            float: The distance in kilometers.
        """

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
        measure_indicators
    ) -> dict[tuple,float]:
        """
        Build the input for the interpolator by mapping coordinates to values.

        Args:
            area_discretization (list[list]): The discretized area coordinates.
            measure_indicators: The list of indicator measures.

        Returns:
            dict[tuple, float]: A mapping of coordinates to values.
        """

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
        measure_indicators
    ) -> list:
        """
        Fill known points in the interpolator input with their measured values.

        Args:
            area_discretization (list): The list of discretized coordinates.
            y (list): The list which should be filled with values.
            measure_indicators: The list of indicator measures.

        Returns:
            list: The updated list of values.
        """

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
        """
        Find the closest point in the discretized area to a station's coordinates.

        Args:
            area_discretization (list[tuple]): The list of discretized coordinates.
            station_coordinates (tuple): The coordinates of the station.

        Returns:
            int: The index of the closest point.
        """
        
        min_dist = float("inf")
        min_dist_index = None

        for i in range(len(area_discretization)):
            point = area_discretization[i]
            dist = math.sqrt((point[0] - station_coordinates[0]) ** 2 + (point[1] - station_coordinates[1]) ** 2)
            if dist < min_dist:
                min_dist_index = i
                min_dist = dist
        
        return min_dist_index




