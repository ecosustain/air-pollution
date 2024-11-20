from models import MeasureIndicator
from sqlalchemy import extract, func


class MeasureIndicatorRepository:
    """
    Repository for interacting with the MeasureIndicator table in the database.
    Provides methods to retrieve aggregated indicator data based on specified filters.
    """

    def __init__(self, session) -> None:
        """
        Initialize the repository with a database session.
        
        Args:
            session: The database session used to execute queries.
        """
        self.session = session
    
    def get_mean_measure_indicators(
        self,
        indicator_id: int,
        time_reference_str: str
    ) -> list[tuple]:
        """
        Retrieve the mean values of measure indicators grouped by station for a specific indicator and time period.

        Args:
            indicator_id (int): The ID of the indicator to filter by.
            time_reference_str (str): A string representing the time reference (e.g., "2024", "2024-11", "2024-11-19 14").

        Returns:
            list[tuple]: A list of tuples, where each tuple contains:
                - idStation (int): The ID of the station.
                - value (float): The average value of the indicator at the station.
        """

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

    @staticmethod
    def __process_date_filters(query, time_reference: str):
        """
        Apply date and time filters to a query based on the provided time reference string.

        Args:
            query: The SQLAlchemy query object to filter.
            time_reference (str): A string representing the time reference (e.g., "2024", "2024-11", "2024-11-19 14").

        Returns:
            The query object with applied filters for year, month, day, and/or hour.
        """
        
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

    def get_measure_indicator_by_year(self, indicator_id: int) -> list[dict]:
        """
            Returns the average 'value' of MeasureIndicators grouped by year for a specific indicator_id.
        """
        results = (
            self.session.query(
                func.extract('year', MeasureIndicator.datetime).label('year'),
                func.avg(MeasureIndicator.value).label('average_value')
            )
            .filter(MeasureIndicator.idIndicator == indicator_id)
            .group_by(func.extract('year', MeasureIndicator.datetime))
            .all()
        )

        return [{"year": int(row.year), "average_value": row.average_value} for row in results]

    def get_measure_indicator_by_month_through_years(self, month: int, indicator_id: int) -> list[dict]:
        """
            Returns the average 'value' of MeasureIndicators grouped by year, filtered by month,
            for a specific indicator_id.
        """
        results = (
            self.session.query(
                func.extract('year', MeasureIndicator.datetime).label('year'),
                func.avg(MeasureIndicator.value).label('average_value')
            )
            .filter(func.extract('month', MeasureIndicator.datetime) == month)
            .filter(MeasureIndicator.idIndicator == indicator_id)
            .group_by(func.extract('year', MeasureIndicator.datetime))
            .all()
        )

        return [{"year": int(row.year), "average_value": row.average_value} for row in results]

    def get_measure_indicator_averaged_per_month_for_all_years(self, indicator_id) -> list[dict]:
        """
            Returns the average 'value' of MeasureIndicators grouped by month for a specific indicator_id.
        """
        results = (
            self.session.query(
                func.extract('month', MeasureIndicator.datetime).label('month'),
                func.avg(MeasureIndicator.value).label('average_value')
            )
            .filter(MeasureIndicator.idIndicator == indicator_id)
            .group_by(func.extract('month', MeasureIndicator.datetime))
            .order_by(func.extract('month', MeasureIndicator.datetime))
            .all()
        )

        return [{"month": int(row.month), "average_value": row.average_value} for row in results]

    def get_measure_indicator_by_day(self, year: int, month: int, indicator_id: int) -> list[dict]:
        """
        Returns the average 'value' of MeasureIndicators grouped by day, filtered by year and month,
        for a specific indicator_id.
        """
        results = (
            self.session.query(
                func.extract('day', MeasureIndicator.datetime).label('day'),
                func.avg(MeasureIndicator.value).label('average_value')
            )
            .filter(func.extract('year', MeasureIndicator.datetime) == year)
            .filter(func.extract('month', MeasureIndicator.datetime) == month)
            .filter(MeasureIndicator.idIndicator == indicator_id)
            .group_by(func.extract('day', MeasureIndicator.datetime))
            .all()
        )

        return [{"day": int(row.day), "average_value": row.average_value} for row in results]

    def get_measure_indicator_by_hour(self, month: int, indicator_id: int) -> list[dict]:
        """
        Returns the average 'value' of MeasureIndicators grouped by hour (from 00:00 to 23:00),
        filtered by month, for a specific indicator_id.
        """
        hour_column = func.extract('hour', MeasureIndicator.datetime).label('hour')

        results = (
            self.session.query(
                hour_column,
                func.avg(MeasureIndicator.value).label('average_value')
            )
            .filter(func.extract('month', MeasureIndicator.datetime) == month)
            .filter(MeasureIndicator.idIndicator == indicator_id)
            .group_by(hour_column)
            .order_by(hour_column)
            .all()
        )

        return [{"hour": int(row.hour), "average_value": row.average_value} for row in results]
