import pandas as pd
import requests
from datetime import datetime
from utils.credentials import LOGIN_QUALAR, PASSWORD_QUALAR

def get_session_id():
    """
    Retrieves the session ID from the cookies obtained after authenticating to CETESB Qualar.

    This function calls `access_qualar` to perform authentication and fetches the cookies. 
    It then extracts and returns the value of the last cookie, which is assumed to be the session ID.

    Returns:
        str: The session ID extracted from the cookies.

    Notes:
        - The method currently assumes that the last cookie in the cookies jar is the session ID.
        - If no cookies are returned or the structure of the cookies changes, this method may fail
          to retrieve the correct session ID.
    """
    cookies = access_qualar()
    session_id = None
    for cookie in cookies:
        session_id = cookie.value
    return session_id

def access_qualar():
    """
    Authenticates to the CETESB Qualar platform and retrieves the session cookies.

    This function sends a POST request to the CETESB Qualar authenticator endpoint
    with the provided login credentials (stored in the constants `LOGIN_QUALAR` 
    and `PASSWORD_QUALAR`). Upon successful authentication, it returns the 
    session cookies which can be used for subsequent authenticated requests.

    Returns:
        requests.cookies.RequestsCookieJar: The cookies received from the 
        authentication response, containing the session information.
    """
    url = 'https://qualar.cetesb.sp.gov.br/qualar/autenticador'
    payload = {
        'cetesb_login': LOGIN_QUALAR,
        'cetesb_password': PASSWORD_QUALAR,
        'enviar': 'OK'
    }
    response = requests.post(url, data=payload)
    return response.cookies

def get_request_response(session_id, start_date, end_date, station, indicator):
    """
    Sends a POST request to the CETESB Qualar platform to retrieve data based on specified parameters.

    This function constructs and sends a request to the CETESB Qualar API, using the provided session ID,
    date range, station, and indicator. It returns the response text if the request is successful, 
    or `None` if the dates are invalid or the response indicates an error.

    Parameters:
        session_id (str): The session ID obtained from `get_session_id`, used for authentication.
        start_date (str): The start date for the data query in the format "DD/MM/YYYY".
        end_date (str): The end date for the data query in the format "DD/MM/YYYY".
        station (int): The station identifier for which data is being requested.
        indicator (int): The indicator parameter identifier for the requested data.

    Returns:
        str or None: The response text from the server containing the requested data, or `None` if:
            - The date range is invalid.
            - The server response contains an HTML error page.
    """
    if not check_valid_dates(start_date, end_date):
        return None
    url = "https://qualar.cetesb.sp.gov.br/qualar/exportaDadosAvanc.do?method=exportar"
    headers = {'Cookie': f"JSESSIONID={session_id}"}
    payload = {'dataInicialStr': start_date,
               'dataFinalStr': end_date,
               'estacaoVO.nestcaMonto': station,
               'nparmtsSelecionados': indicator}
    
    response = requests.post(url, headers=headers, data=payload)
    if "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\">" in response.text:
        return None
    return response.text


def check_valid_dates(start_date, end_date):
    """
    Validates if the given date range is valid.

    This function checks whether the `end_date` is later than the `start_date`. 
    Both dates should be in the format "DD/MM/YYYY". If the format is incorrect 
    or the conversion fails, the function returns `False`.

    Parameters:
        start_date (str): The start date in the format "DD/MM/YYYY".
        end_date (str): The end date in the format "DD/MM/YYYY".

    Returns:
        bool: `True` if the date range is valid, `False` otherwise.
    """
    try:
        start_date_obj = datetime.strptime(start_date, "%d/%m/%Y")
        end_date_obj = datetime.strptime(end_date, "%d/%m/%Y")
        return end_date_obj > start_date_obj
    except ValueError:
        return False


def string_to_float(value):
    """
    Converts a string representation of a number with a comma as the decimal separator
    to a standard float-compatible string format with a dot as the decimal separator.

    Parameters:
        value (str or any): The value to convert. If it's not a string, it will be
                            converted to a string first.

    Returns:
        str: The value with commas replaced by dots.
    """
    return str(value).replace(",", ".")


def ddmmyyyyhhmm_yyyymmddhhmm(value):
    """
    Converts a datetime string from "DD/MM/YYYY HH:MM" format to "YYYY/MM/DD HH:MM" format.

    This function splits the input value into date and time, reorders the date components, 
    and concatenates them with the time.

    Parameters:
        value (str): A datetime string in the format "DD/MM/YYYY HH:MM".

    Returns:
        str: The converted datetime string in the format "YYYY/MM/DD HH:MM".
    """
    date, hour = str(value).split(" ")
    day, month, year = date.split("/")
    return year + "/" + month + "/" + day + " " + hour


def generate_date_range_df(maximum_date):
    """
    Generates a Pandas DataFrame containing an hourly datetime range 
    from January 1, 2000, 00:00 to the given maximum date and time.

    The resulting DataFrame contains a single column, `datetime`, 
    which is sorted in ascending order.

    Parameters:
        maximum_date (datetime): The maximum date and time for the range.

    Returns:
        pandas.DataFrame: A DataFrame with a `datetime` column containing 
                          the hourly range.
    """
    date_range_hourly = pd.date_range(start='2000-01-01 00:00',
                                      end=maximum_date.strftime('%Y/%m/%d %H:%M'), freq='H')
    df_hourly = pd.DataFrame(date_range_hourly, columns=['datetime'])
    df_hourly['datetime'] = pd.to_datetime(df_hourly['datetime'])
    df_hourly.sort_values(by="datetime", ascending=True, inplace=True)
    return df_hourly
