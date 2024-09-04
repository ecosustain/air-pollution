import requests
from meta_data import stations, indicators
from credentials import login, password


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


def get_data(session_id, interval_years=(2000, 2024)):
    url = "https://qualar.cetesb.sp.gov.br/qualar/exportaDadosAvanc.do?method=exportar"

    cookie_value = f"JSESSIONID={session_id}"
    headers = {
        'Cookie': cookie_value
    }

    for station in stations:
        for indicator in indicators:
            for year in range(interval_years[1], interval_years[0], -1):
                payload = {
                    'dataInicialStr': f"01/01/{year - 1}",
                    'dataFinalStr': f"01/01/{year}",
                    'estacaoVO.nestcaMonto': stations[station],
                    'nparmtsSelecionados': indicators[indicator],
                }

                response = requests.post(url, headers=headers, data=payload)
                if not ("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\">" in response.text):
                    save_csv_file(response.text, station, indicator, str(year - 1), str(year))


def save_csv_file(data, station_name, indicator_name, start_year, end_year):
    fp = open(f"./scrapped_data/{station_name}_{indicator_name}_{start_year}_{end_year}.csv", "w")
    fp.write(data)
    fp.close()


get_data(get_session_id())
