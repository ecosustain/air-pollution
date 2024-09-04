import pandas as pd


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
    # Generate a new datetime DataFrame with hourly intervals from January 1, 2000, to December 31, 2024
    date_range_hourly = pd.date_range(start='2000-01-01 00:00', end='2024-12-31 23:00', freq='H')

    # Create a DataFrame with the new date range
    df_hourly = pd.DataFrame(date_range_hourly, columns=['datetime'])

    # Convert to the desired format "year/month/day hh:00"
    df_hourly['datetime'] = df_hourly['datetime'].dt.strftime('%Y/%m/%d %H:00')

    df_hourly['datetime'] = df_hourly['datetime'].astype(str)
    df_hourly['datetime'] = df_hourly['datetime'].map(mapper)
    df_hourly.sort_values(by="datetime", ascending=True, inplace=True)

    return df_hourly
