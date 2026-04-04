
import requests
import json

url = "http://127.0.0.1:5000/signup"
payload = {"name": "Test", "email": "test@example.com", "password": "Password123!"}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
    print("Status Code:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Error:", e)
