from requests import request

base_url = "http://127.0.0.1:5000"
headers = {}
headers['Content-Type'] = 'application/json'

endpoint = f"/login"
method = "POST"
method = method

url = f"{base_url}{endpoint}"
response = request(
    method.upper(),
    url,
    headers=headers,
)
print(response.status_code)
print(response.json())