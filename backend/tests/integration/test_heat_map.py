from requests import request
from datetime import datetime
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from constants_test import (
    BASE_URL,
    HEADERS,
)

class TestRequest:
    def test_get_map(self):
        endpoint = f"/heat_map"
        method = "GET"

        initial_date = datetime(2023, 3, 1, 12, 10)
        final_date = datetime(2023, 3, 1, 13, 10)

        indicator = "MP2.5"

        PARAM_DICT = {
            "method": ["ordinary", "universal"],
            "variogram_model": ["linear", "power", "gaussian", "spherical"],
            "nlags": [4, 6, 8],
            "weight": [True, False]
        }

        interpolator = ("KrigingInterpolator", PARAM_DICT)

        payload = {
            "initial_date": initial_date.strftime('%Y-%m-%d %H:%M:%S'),
            "final_date": final_date.strftime('%Y-%m-%d %H:%M:%S'),
            "indicator": indicator,
            "interpolator": interpolator,
        }

        url = f"{BASE_URL}{endpoint}"
        response = request(
            method.upper(),
            url,
            headers=HEADERS,
            json=payload
        )

        assert response.status_code == 200
        assert len(response.json()) > 0