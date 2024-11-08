from repositories import (
    MeasureIndicatorRepository
)

from models import (
    MeasureIndicator
)

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from metadata.meta_data import INDICATORS, STATIONS_ID


# Maybe using ENUM would be the "best practice" way to implement it;
INTERVAL_POSSIBILITIES = ["yearly",  "monthly", "daily", "hourly"]


class LineGraphController:
    def __init__(self, session) -> None:
        self.measure_indicator_repository = MeasureIndicatorRepository(session)
        self.session = session

    def get_line_graph(
            self,
            payload: dict
    ) -> list[dict]:

        if self.validate_payload_format(payload):
            indicators = payload["indicators"]
            indicator_ids = []
            for indicator in indicators:
                indicator_ids.append(INDICATORS[indicator])

            interval = payload["interval"]
            if not (interval in INTERVAL_POSSIBILITIES):
                return []

            if interval == "monthly":
                month = payload["month"]
                response = []
                for indicator_index, indicator_id in enumerate(indicator_ids):
                    response.append({f"{indicators[indicator_index]}":
                        self.measure_indicator_repository.get_measure_indicator_by_month(month=month,
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

    @staticmethod
    def validate_payload_format(payload: dict) -> bool:
        """Checks if payload format is correct returning true or false"""
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

            if interval == "monthly":
                month = payload["month"]

            elif interval == "daily":
                month = payload["month"]
                year = payload["year"]

            elif interval == "hourly":
                month = payload["month"]

            elif interval == "yearly":
                pass

            else:
                pass

        except Exception as e:
            print(e)
            return False

        return True
