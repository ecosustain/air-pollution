from requests import request
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from constants_test import (
    BASE_URL,
    HEADERS,
)

class TestRequest:
    def test_get_map(self):
        endpoint = f"/"
        method = "GET"

        url = f"{BASE_URL}{endpoint}"
        response = request(
            method.upper(),
            url,
            headers=HEADERS,
        )

        assert response.status_code == 200