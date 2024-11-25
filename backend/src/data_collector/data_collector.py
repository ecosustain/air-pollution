import os
from utils.utils import get_session_id, get_request_response
from metadata.meta_data import STATIONS, INDICATORS


def get_data(session_id, interval_years=(2000, 2024), interval_size=1):
    """
    Collects and saves data for specified stations and indicators over a range of years.

    This function iterates through the list of stations and indicators, making data requests for 
    each combination within the given year range. The data is requested in intervals defined by 
    `interval_size` and saved as CSV files for each interval.

    Parameters:
        session_id (str): The session ID for authenticating requests to the CETESB Qualar platform.
        interval_years (tuple, optional): A tuple specifying the range of years for data collection 
                                          in the format `(start_year, end_year)`. Defaults to `(2000, 2024)`.
        interval_size (int, optional): The size of the year intervals for data collection. Defaults to `1`.
    """
    for station in STATIONS:
        for indicator in INDICATORS:
            for year in range(interval_years[1], interval_years[0], -interval_size):
                print(f"Collecting data: {station} - {indicator} - {year - interval_size}:{year}")
                start_date = f"01/01/{year - interval_size}"
                end_date = f"01/01/{year}"
                response_text = get_request_response(session_id, start_date, end_date,
                                                     STATIONS[station][0], INDICATORS[indicator])
                if response_text is not None:
                    save_csv_file(response_text, station, indicator, str(year - interval_size), str(year))
                    print(f"Succesfully saved: {station} - {indicator} - {year - interval_size}:{year}")


def save_csv_file(data, station_name, indicator_name, start_year, end_year):
    """
    Saves data to a CSV file in a specified directory, creating the directory if it does not exist.

    This function writes the provided `data` to a CSV file. The file is named using the 
    `station_name`, `indicator_name`, `start_year`, and `end_year` parameters, and is saved 
    in the `./backend/data/collected_csvs` directory.

    Parameters:
        data (str): The content to be written to the CSV file, typically in CSV format.
        station_name (str): The name of the station associated with the data.
        indicator_name (str): The name of the indicator associated with the data.
        start_year (str): The start year for the data.
        end_year (str): The end year for the data.
    """
    directory = "./backend/data/collected_csvs"
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = f"{directory}/{station_name}_{indicator_name}_{start_year}_{end_year}.csv"
    with open(file_path, "w") as fp:
        fp.write(data)


if __name__ == "__main__":
    get_data(get_session_id(), interval_size=8)
