from requests import request

from constants_test import (
    BASE_URL,
    HEADERS
)

class TestRequest:
    def test_get_map(self):
        endpoint = f"/login"
        method = "POST"

        url = f"{BASE_URL}{endpoint}"
        response = request(
            method.upper(),
            url,
            headers=HEADERS,
        )

        assert response.status_code == 201
        assert "teste" in response.json() 