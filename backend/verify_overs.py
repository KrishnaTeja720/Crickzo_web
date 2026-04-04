import requests
import json
import time

BASE_URL = "http://127.0.0.1:5005"

def test_manual_overs():
    # 1. Create 6-over match
    payload = {
        "user_id": 1,
        "team_a": "VerifyA",
        "team_b": "VerifyB",
        "format": "6", # 6 Overs
        "venue": "Test",
        "toss": "VerifyA",
        "toss_decision": "Batting",
        "pitch": "Batting",
        "weather": "Clear"
    }
    
    print(f"Creating match with format: {payload['format']} Overs...")
    res = requests.post(f"{BASE_URL}/match/create", json=payload)
    if res.status_code != 200:
        print(f"Error creating match: {res.text}")
        return
    
    match_id = res.json().get("match_id")
    print(f"Match created! ID: {match_id}")
    
    # 2. Add players (needed for prediction striker/bowler)
    # We'll use existing player API if possible, or just set current players
    # Actually, predictions might work even with default 'Striker'/'Bowler' names if they are in DB
    
    # 3. Add 1 ball to trigger 1.4x par calculation
    ball_payload = {
        "match_id": match_id,
        "innings": 1,
        "batsman": "Striker",
        "bowler": "Bowler",
        "runs": 1,
        "extras": 0,
        "wicket": 0,
        "is_wicket": False
    }
    print("Recording first ball (1 run)...")
    requests.post(f"{BASE_URL}/match/ball", json=ball_payload)
    
    # 4. Fetch predictions
    print("Fetching predictions...")
    pred_res = requests.get(f"{BASE_URL}/match/predictions/{match_id}?innings=1")
    pred_data = pred_res.json()
    
    projected_score = pred_data.get("projected_score", {})
    range_val = projected_score.get("range", "N/A")
    
    print(f"Projected Score Range: {range_val}")
    
    # Expected: max_balls * 1.4 = 36 * 1.4 = 50.4.
    # Prediction range is +/- 7/8 around projected. So roughly 43-58.
    # If it was T20 (120 balls), it would be 120 * 1.4 = 168. Range ~161-176.
    
    if "16" in range_val:
        print("FAILURE: Prediction seems to be using T20 balls (120) instead of 6 overs (36).")
    elif "4" in range_val or "5" in range_val:
        print("SUCCESS: Prediction is correctly using 6 overs (36 balls)!")
    else:
        print(f"UNSURE: Got range {range_val}. Please inspect manually.")

if __name__ == "__main__":
    test_manual_overs()
