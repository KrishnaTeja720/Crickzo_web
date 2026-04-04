import requests
import json

BASE_URL = "http://127.0.0.1:5000"
USER_ID = 1

def test_upcoming_flow():
    # 1. Create a match
    match_data = {
        "user_id": USER_ID,
        "team_a": "Upcoming Bug",
        "team_b": "Live Test",
        "format": "T20",
        "toss": "Upcoming Bug",
        "toss_decision": "Batting",
        "pitch": "Dry",
        "weather": "Sunny"
    }
    resp = requests.post(f"{BASE_URL}/match/create", json=match_data)
    match_id = resp.json().get("match_id")
    print(f"Created Match ID: {match_id}")

    # 2. Start match
    start_data = {
        "match_id": match_id,
        "striker": "S1",
        "non_striker": "NS1",
        "bowler": "B1"
    }
    resp = requests.post(f"{BASE_URL}/match/start", json=start_data)
    print(f"Start Match Response: {resp.text}")

    # 3. Record ball
    ball_data = {
        "match_id": match_id,
        "runs": 0,
        "is_wicket": False,
        "striker": "S1",
        "non_striker": "NS1",
        "bowler": "B1"
    }
    resp = requests.post(f"{BASE_URL}/ball_input", json=ball_data)
    print(f"Ball Input Response: {resp.text}")

    # 4. Check categorization
    resp_upcoming = requests.get(f"{BASE_URL}/matches/upcoming?user_id={USER_ID}")
    resp_live = requests.get(f"{BASE_URL}/matches/live?user_id={USER_ID}")
    
    in_upcoming = any(m['match_id'] == match_id for m in resp_upcoming.json())
    in_live = any(m['match_id'] == match_id for m in resp_live.json())
    
    print(f"Match {match_id} - In Upcoming: {in_upcoming}, In Live: {in_live}")

if __name__ == "__main__":
    test_upcoming_flow()
