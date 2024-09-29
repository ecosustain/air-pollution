from requests import request

base_url = "http://127.0.0.1:5000"
headers = {}
headers['Content-Type'] = 'application/json'

class TestRequest:
    def test_get_map(self):
        endpoint = f"/login"
        method = "POST"

        url = f"{base_url}{endpoint}"
        response = request(
            method.upper(),
            url,
            headers=headers,
        )

        assert response.status_code == 201
        assert "teste" in response.json() 