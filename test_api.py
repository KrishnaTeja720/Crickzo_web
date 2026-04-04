import requests
import json

def test_ball():
    url = "http://localhost:5000/match/ball"
    payload = {
        "match_id": 75,
        "innings": 1,
        "runs": 1,
        "is_wicket": False
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ball()
