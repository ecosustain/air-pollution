from requests import request

from constants_test import (
    BASE_URL,
    HEADERS,
)

class TestRequest:
    def test_get_map(self):
        endpoint = f"/heat_map"
        method = "GET"

        url = f"{BASE_URL}{endpoint}"
        response = request(
            method.upper(),
            url,
            headers=HEADERS,
        )

        assert response.status_code == 200
        assert "idStation" in response.json()[0] 