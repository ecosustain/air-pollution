from repositories import MeasureIndicatorRepository
from metadata.meta_data import INDICATORS, STATIONS_ID


# Maybe using ENUM would be the "best practice" way to implement it;
INTERVAL_POSSIBILITIES = ["yearly",  "monthly", "daily", "hourly"]


class LineGraphController:
    """
    Controller class responsible for fetching and formatting data for line graph visualizations.
    """
    def __init__(self, session) -> None:
        """
        Initializes the controller with a database session and repository for querying data.

        Args:
            session: Database session object used to interact with the database.
        """
        self.measure_indicator_repository = MeasureIndicatorRepository(session)
        self.session = session

    def get_line_graph(
            self,
            payload: dict
    ) -> list[dict]:
        """
        Fetches line graph data based on the input payload.

        Args:
            payload (dict): A dictionary containing the following keys:
                - "indicators" (list[str]): List of indicators to query.
                - "interval" (str): The interval of aggregation ("yearly", "monthly", "daily", or "hourly").
                - Optional keys depending on the interval:
                  - "month" (int): The month for data filtering (1-12).
                  - "year" (int): The year for data filtering (e.g., 2024).

        Returns:
            list[dict]: A list of dictionaries containing the requested data for each indicator.
        """
        if self.validate_payload_format(payload):
            indicators = payload["indicators"]
            indicator_ids = []
            for indicator in indicators:
                indicator_ids.append(INDICATORS[indicator])

            interval = payload["interval"]
            if not (interval in INTERVAL_POSSIBILITIES):
                return []

            if interval == "monthly":
                if "month" in payload.keys():
                    month = payload["month"]
                    response = []
                    for indicator_index, indicator_id in enumerate(indicator_ids):
                        response.append({f"{indicators[indicator_index]}":
                            self.measure_indicator_repository.get_measure_indicator_by_month_through_years(month=month,
                                                                                             indicator_id=indicator_id)
                                         })
                else:
                    response = []
                    for indicator_index, indicator_id in enumerate(indicator_ids):
                        response.append({f"{indicators[indicator_index]}":
                                             self.measure_indicator_repository.get_measure_indicator_averaged_per_month_for_all_years(
                                                 indicator_id=indicator_id)
                                         })

            elif interval == "daily":
                month = payload["month"]
                year = payload["year"]

                response = []
                for indicator_index, indicator_id in enumerate(indicator_ids):
                    response.append({f"{indicators[indicator_index]}":
                                         self.measure_indicator_repository.get_measure_indicator_by_day(month=month,
                                                                                                        year=year,
                                                                                                        indicator_id=indicator_id)
                                     })

            elif interval == "hourly":
                month = payload["month"]
                response = []
                for indicator_index, indicator_id in enumerate(indicator_ids):
                    response.append({f"{indicators[indicator_index]}":
                                         self.measure_indicator_repository.get_measure_indicator_by_hour(month=month,
                                                                                                         indicator_id=indicator_id)
                                     })

            elif interval == "yearly":
                response = []
                for indicator_index, indicator_id in enumerate(indicator_ids):
                    response.append({f"{indicators[indicator_index]}":
                                         self.measure_indicator_repository.get_measure_indicator_by_year(indicator_id=indicator_id)
                                     })

            else:
                response = []
        else:
            response = []

        return response

    def validate_payload_format(self, payload: dict) -> bool:
        """
        Validates the format of the input payload.

        Args:
            payload (dict): Payload dictionary to validate.

        Returns:
            bool: True if the payload format is valid, False otherwise.
        """
        try:
            # Validate indicators
            indicators = payload["indicators"]
            indicator_ids = []
            for indicator in indicators:
                indicator_ids.append(INDICATORS[indicator])

            # Validate interval
            interval = payload["interval"]
            if not (interval in INTERVAL_POSSIBILITIES):
                return False

            elif interval == "daily":
                month = payload["month"]
                year = payload["year"]

                if (not self.is_valid_month(month)) or (not self.is_valid_year(year)):
                    return False

            elif interval == "hourly":
                month = payload["month"]
                if not self.is_valid_month(month):
                    return False

            elif interval == "yearly":
                pass

            else:
                pass

        except Exception as e:
            print(e)
            return False

        return True

    @staticmethod
    def is_valid_month(month):
        if month is None:
            return False

        if type(month) == int:
            if 1 <= month <= 12:
                return True

        return False

    @staticmethod
    def is_valid_year(year):
        if year is None:
            return False

        if type(year) == int:
            if 2000 <= year <= 2100:
                return True

        return False
