
import requests

url = "http://127.0.0.1:5000/test/echo"
try:
    response = requests.get(url, timeout=5)
    print("Status Code:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Error:", e)
