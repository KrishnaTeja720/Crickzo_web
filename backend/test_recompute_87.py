
import requests
import json

url = "http://localhost:5000/match/recompute_score"
payload = {"match_id": 87, "innings": 1}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)
except Exception as e:
    print("Error:", e)
