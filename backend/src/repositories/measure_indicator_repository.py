from models import MeasureIndicator

import datetime
from sqlalchemy import extract,func

class MeasureIndicatorRepository:
    def __init__(self, session) -> None:
        self.session = session
    
    def get_mean_measure_indicators(
        self,
        indicator_id: int,
        time_reference_str: str
    ) -> list[tuple]:
        
        query = (
            self.session.query(
                MeasureIndicator.idStation,
                func.avg(MeasureIndicator.value).label('value')
            )
            .filter(MeasureIndicator.idIndicator == indicator_id)
        )

        query = self.__process_date_filters(query, time_reference_str)

        result = (
            query.group_by(
                MeasureIndicator.idStation
            )
            .all()
        )   

        return result
    
    def __process_date_filters(self, query, time_reference: str):
        year, month, day, hour = None, None, None, None
        datetime_list = time_reference.split(" ")

        date_list = datetime_list[0].split("-")
        year = date_list[0]
        if len(date_list) > 1:
            month = date_list[1]
            if len(date_list) > 2:
                day = date_list[2]

        if len(datetime_list) > 1:
            time_list = datetime_list[1].split(":")
            hour = time_list[0]

        if year:
           query = query.filter(extract("year", MeasureIndicator.datetime) == year)
        if month:
           query = query.filter(extract("month", MeasureIndicator.datetime) == month)
        if day:
           query = query.filter(extract("day", MeasureIndicator.datetime) == day)
        if hour:
           query = query.filter(extract("hour", MeasureIndicator.datetime) == hour)

        return query