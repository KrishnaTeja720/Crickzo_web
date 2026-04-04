import requests
import json

urls = ["http://localhost:5000/match/refresh_score", "http://localhost:5000/match/refresh_score/"]
payload = {"match_id": 87, "innings": 1}
headers = {"Content-Type": "application/json"}

for url in urls:
    print(f"Testing URL: {url}")
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
        print("Status Code:", response.status_code)
        print("Response Text:", response.text[:100])
        if response.status_code == 200:
            print("Response JSON:", response.json())
    except Exception as e:
        print("Error:", e)
