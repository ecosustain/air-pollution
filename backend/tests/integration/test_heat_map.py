from requests import request
from datetime import datetime
import sys, os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from constants_test import (
    BASE_URL,
    HEADERS,
)

class TestRequest:
    def test_get_map(self):
        method = "GET"

        date = datetime(2023, 3, 1, 12)

        indicator = "MP2.5"

        PARAM_DICT = {
            "method": ["ordinary", "universal"],
            "variogram_model": ["linear", "power", "gaussian", "spherical"],
            "nlags": [4, 6, 8],
            "weight": [True, False]
        }

        interpolator = {
            "method": "Kriging",
            "params": PARAM_DICT,
        }

        payload = {
            "datetime": date.strftime('%Y-%m-%d %H:%M:%S'),
            "indicator": indicator,
            "interpolator": interpolator,
        }
        payload_str = json.dumps(payload)
     
        endpoint = f"/heat_map/{payload_str}"
        url = f"{BASE_URL}{endpoint}"
        response = request(
            method.upper(),
            url,
            headers=HEADERS,
            json=payload
        )

        assert response.status_code == 200
        assert len(response.json()) > 0

        item = response.json()["heat_map"][0]
        assert "lat" in item
        assert "long" in item
        assert "value" in item

    def test_update(self):
        method = "PUT"

        endpoint = f"/update_data"
        url = f"{BASE_URL}{endpoint}"
        response = request(
            method.upper(),
            url,
            headers=HEADERS,
        )

        assert response.status_code == 200