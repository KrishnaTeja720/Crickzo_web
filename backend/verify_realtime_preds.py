import requests

match_id = 89
url = f"http://127.0.0.1:5005/match/state/{match_id}"

try:
    response = requests.get(url)
    data = response.json()
    print("API RESPONSE RECEIVED")
    if "predictions" in data:
        print("PREDICTIONS FOUND IN RESPONSE")
        print(data["predictions"])
    else:
        print("PREDICTIONS MISSING")
except Exception as e:
    print(f"ERROR: {e}")
