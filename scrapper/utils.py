import pandas as pd
import requests
from datetime import datetime

from credentials import login_qualar, password_qualar

def get_session_id():
    cookies = access_qualar()
    session_id = None
    for cookie in cookies:
        session_id = cookie.value
    return session_id

def access_qualar():
    url = 'https://qualar.cetesb.sp.gov.br/qualar/autenticador'
    payload = {
        'cetesb_login': login_qualar,
        'cetesb_password': password_qualar,
        'enviar': 'OK'
    }
    response = requests.post(url, data=payload)
    return response.cookies

def get_request_response(session_id, start_date, end_date, station, indicator):
    if not check_valid_dates(start_date, end_date):
        return None
    url = "https://qualar.cetesb.sp.gov.br/qualar/exportaDadosAvanc.do?method=exportar"
    headers = {'Cookie': f"JSESSIONID={session_id}"}
    payload = { 'dataInicialStr': start_date,
                'dataFinalStr': end_date,
                'estacaoVO.nestcaMonto': station,
                'nparmtsSelecionados': indicator    }
    
    response = requests.post(url, headers=headers, data=payload)
    if ("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\">" in response.text):
        return None
    return response.text

def check_valid_dates(start_date, end_date):
    try:
        start_date_obj = datetime.strptime(start_date, "%d/%m/%Y")
        end_date_obj = datetime.strptime(end_date, "%d/%m/%Y")
        return end_date_obj > start_date_obj
    except ValueError:
        return False

def string_to_float(value):
    return str(value).replace(",", ".")

def mapper(value):
    date, hour = str(value).split(" ")
    if hour == "00:00":
        hour = "24:00"

    year, month, day = date.split("/")
    return year + "/" + month + "/" + day + " " + hour

def ddmmyyyyhhmm_yyyymmddhhmm(value):
    date, hour = str(value).split(" ")
    day, month, year = date.split("/")
    return year + "/" + month + "/" + day + " " + hour

def generate_date_range_df():
    date_range_hourly = pd.date_range(start='2000-01-01 00:00', end='2024-12-31 23:00', freq='H')
    df_hourly = pd.DataFrame(date_range_hourly, columns=['datetime'])
    df_hourly['datetime'] = df_hourly['datetime'].dt.strftime('%Y/%m/%d %H:00')
    df_hourly['datetime'] = df_hourly['datetime'].astype(str)
    df_hourly['datetime'] = df_hourly['datetime'].map(mapper)
    df_hourly.sort_values(by="datetime", ascending=True, inplace=True)
    return df_hourly
