from utils.utils import get_session_id, get_request_response
from metadata.meta_data import STATIONS, INDICATORS
import os


def get_data(session_id, interval_years=(2000, 2024), interval_size=1):
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
    directory = "./backend/data/collected_csvs"
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = f"{directory}/{station_name}_{indicator_name}_{start_year}_{end_year}.csv"
    with open(file_path, "w") as fp:
        fp.write(data)


if __name__ == "__main__":
    get_data(get_session_id(), interval_size=8)
