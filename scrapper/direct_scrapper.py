import requests
from credentials import login, password
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from metadata.meta_data import stations, indicators


def get_session_id():
    url = 'https://qualar.cetesb.sp.gov.br/qualar/autenticador'
    payload = {
        'cetesb_login': login,
        'cetesb_password': password,
        'enviar': 'OK'
    }

    # Send a POST request with application/x-www-form-urlencoded
    response = requests.post(url, data=payload)
    cookies = response.cookies

    # Print the cookies
    session_id = None
    for cookie in cookies:
        session_id = cookie.value

    return session_id


def get_data(session_id, interval_years=(2000, 2024), interval_size=1):
    url = "https://qualar.cetesb.sp.gov.br/qualar/exportaDadosAvanc.do?method=exportar"

    cookie_value = f"JSESSIONID={session_id}"
    headers = {
        'Cookie': cookie_value
    }

    for station in stations:
        for indicator in indicators:
            for year in range(interval_years[1], interval_years[0], -interval_size):
                payload = {
                    'dataInicialStr': f"01/01/{year - interval_size}",
                    'dataFinalStr': f"01/01/{year}",
                    'estacaoVO.nestcaMonto': stations[station][0],
                    'nparmtsSelecionados': indicators[indicator],
                }

                response = requests.post(url, headers=headers, data=payload)
                if not ("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\">" in response.text):
                    save_csv_file(response.text, station, indicator, str(year - interval_size), str(year))
                    print(f"Succesfully saved: {station} - {indicator} - {year - interval_size}:{year}")


def save_csv_file(data, station_name, indicator_name, start_year, end_year):
    directory = "./data/scraped_data"
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = f"{directory}/{station_name}_{indicator_name}_{start_year}_{end_year}.csv"
    with open(file_path, "w") as fp:
        fp.write(data)


get_data(get_session_id(), interval_size=8)
