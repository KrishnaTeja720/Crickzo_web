import requests
import json

BASE_URL = "http://127.0.0.1:5000"
USER_ID = 1

def test_upcoming_flow():
    # 1. Create a match
    match_data = {
        "user_id": USER_ID,
        "team_a": "Upcoming Alpha",
        "team_b": "Upcoming Beta",
        "format": "T20",
        "toss": "Upcoming Alpha",
        "toss_decision": "Batting",
        "pitch": "Dry",
        "weather": "Sunny"
    }
    resp = requests.post(f"{BASE_URL}/match/create", json=match_data)
    match_id = resp.json().get("match_id")
    print(f"Created Match ID: {match_id}")

    # 2. Check upcoming
    resp = requests.get(f"{BASE_URL}/matches/upcoming?user_id={USER_ID}")
    in_upcoming_pre = any(m['match_id'] == match_id for m in resp.json())
    print(f"Match {match_id} - In Upcoming (init): {in_upcoming_pre}")

    # 3. Start match
    start_data = {
        "match_id": match_id,
        "striker": "Player S1",
        "non_striker": "Player NS1",
        "bowler": "Player B1"
    }
    requests.post(f"{BASE_URL}/match/start", json=start_data)

    # 4. Record ball (Corrected URL)
    ball_data = {
        "match_id": match_id,
        "runs": 0,
        "is_wicket": False
    }
    resp = requests.post(f"{BASE_URL}/match/ball", json=ball_data)
    print(f"Ball Input Response: {resp.status_code} - {resp.text}")

    # 5. Check categorization
    resp_upcoming = requests.get(f"{BASE_URL}/matches/upcoming?user_id={USER_ID}")
    resp_live = requests.get(f"{BASE_URL}/matches/live?user_id={USER_ID}")
    
    in_upcoming = any(m['match_id'] == match_id for m in resp_upcoming.json())
    in_live = any(m['match_id'] == match_id for m in resp_live.json())
    
    print(f"Match {match_id} - In Upcoming: {in_upcoming}, In Live: {in_live}")

if __name__ == "__main__":
    test_upcoming_flow()
