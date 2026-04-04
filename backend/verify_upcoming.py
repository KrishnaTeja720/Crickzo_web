import requests
import json

BASE_URL = "http://127.0.0.1:5000"
USER_ID = 1  # Assuming user_id 1 exists

def test_upcoming_flow():
    # 1. Create a match
    match_data = {
        "user_id": USER_ID,
        "team_a": "Alpha Team",
        "team_b": "Beta Team",
        "format": "T20",
        "venue": "Test Stadium",
        "toss": "Alpha Team",
        "toss_decision": "Batting",
        "pitch": "Dry",
        "weather": "Sunny"
    }
    resp = requests.post(f"{BASE_URL}/match/create", json=match_data)
    match_id = resp.json().get("match_id")
    print(f"Created Match ID: {match_id}")

    # 2. Check upcoming matches
    resp = requests.get(f"{BASE_URL}/matches/upcoming?user_id={USER_ID}")
    upcoming = resp.json()
    match_ids = [m['match_id'] for m in upcoming]
    print(f"Upcoming Matches: {match_ids}")
    if match_id in match_ids:
        print("SUCCESS: Match found in Upcoming.")
    else:
        print("FAILURE: Match NOT found in Upcoming.")
        return

    # 3. Start match (set players)
    start_data = {
        "match_id": match_id,
        "striker": "Player 1",
        "non_striker": "Player 2",
        "bowler": "Bowler 1"
    }
    requests.post(f"{BASE_URL}/match/start", json=start_data)
    print("Match started (players set).")

    # 4. Check upcoming again (should still be there because 0 balls)
    resp = requests.get(f"{BASE_URL}/matches/upcoming?user_id={USER_ID}")
    upcoming = resp.json()
    if any(m['match_id'] == match_id for m in upcoming):
        print("SUCCESS: Match still in Upcoming (0 balls).")
    else:
        print("FAILURE: Match missing from Upcoming after start.")

    # 5. Record a ball
    ball_data = {
        "match_id": match_id,
        "runs": 0,
        "extra_type": None,
        "is_wicket": False,
        "striker": "Player 1",
        "non_striker": "Player 2",
        "bowler": "Bowler 1"
    }
    requests.post(f"{BASE_URL}/ball_input", json=ball_data)
    print("First ball recorded.")

    # 6. Check live matches
    resp = requests.get(f"{BASE_URL}/matches/live?user_id={USER_ID}")
    live = resp.json()
    if any(m['match_id'] == match_id for m in live):
        print("SUCCESS: Match moved to Live.")
    else:
        print("FAILURE: Match NOT found in Live.")

    # 7. Check upcoming matches (should be gone)
    resp = requests.get(f"{BASE_URL}/matches/upcoming?user_id={USER_ID}")
    upcoming = resp.json()
    if not any(m['match_id'] == match_id for m in upcoming):
        print("SUCCESS: Match removed from Upcoming.")
    else:
        print("FAILURE: Match still in Upcoming after first ball.")

if __name__ == "__main__":
    test_upcoming_flow()
