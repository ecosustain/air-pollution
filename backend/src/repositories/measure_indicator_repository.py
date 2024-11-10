from models import MeasureIndicator
from sqlalchemy import func
import datetime


class MeasureIndicatorRepository:
    def __init__(self, session) -> None:
        self.session = session

    def get_measure_indicators(
        self,
        date: datetime,
        indicator_id: int
    ) -> list[MeasureIndicator]:
        
        measure_indicators = (self.session.query(MeasureIndicator)
                              .filter(MeasureIndicator.datetime == date)
                              .filter(MeasureIndicator.idIndicator == indicator_id)
                              .all()
                              )
        
        return measure_indicators

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
