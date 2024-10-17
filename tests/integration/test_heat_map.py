from requests import request

from constants_test import (
    BASE_URL,
    HEADERS,
)

from datetime import datetime

class TestRequest:
    def test_get_map(self):
        endpoint = f"/heat_map"
        method = "GET"

        initial_date = datetime(2023, 10, 9, 17, 10)
        final_date = datetime(2023, 10, 9, 18, 10)

        payload = {
            "initial_date": initial_date.strftime('%Y-%m-%d %H:%M:%S'),
            "final_date": final_date.strftime('%Y-%m-%d %H:%M:%S')
        }

        url = f"{BASE_URL}{endpoint}"
        response = request(
            method.upper(),
            url,
            headers=HEADERS,
            json=payload
        )

        assert response.status_code == 200
        assert "idStation" in response.json()[0] 