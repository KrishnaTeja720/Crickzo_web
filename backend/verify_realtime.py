import requests
import json

BASE_URL = "http://127.0.0.1:5005"

def test_first_ball_projection():
    # 1. Create a 20-over match
    payload = {
        "user_id": 1,
        "team_a": "RealTimeA",
        "team_b": "RealTimeB",
        "format": "20",
        "venue": "Test",
        "toss": "RealTimeA",
        "toss_decision": "Batting",
        "pitch": "Batting",
        "weather": "Clear"
    }
    
    print("Creating 20-over match...")
    res = requests.post(f"{BASE_URL}/match/create", json=payload)
    match_id = res.json().get("match_id")
    print(f"Match ID: {match_id}")
    
    # 2. Add 1 ball (6 runs)
    # CRR will be 36.0
    # Projected = 6 + (119 * 6) = 720
    ball_payload = {
        "match_id": match_id,
        "innings": 1,
        "batsman": "Striker",
        "bowler": "Bowler",
        "runs": 6,
        "extras": 0,
        "wicket": 0,
        "is_wicket": False
    }
    print("Recording first ball (6 runs)...")
    requests.post(f"{BASE_URL}/match/ball", json=ball_payload)
    
    # 3. Fetch predictions
    print("Fetching predictions...")
    pred_res = requests.get(f"{BASE_URL}/match/predictions/{match_id}?innings=1")
    pred_data = pred_res.json()
    
    projected_score_range = pred_data.get("projected_score", {}).get("range", "N/A")
    print(f"Projected Score Range: {projected_score_range}")
    
    # If the threshold was still there, it would be 120 * 1.4 = 168.
    # With CRR, it should be around 713-728.
    
    if "7" in projected_score_range and "2" in projected_score_range:
        print("SUCCESS: Projected Total is using CRR from the 1st ball!")
    elif "16" in projected_score_range:
        print("FAILURE: Still using the 12-ball threshold (Par score).")
    else:
        print(f"UNSURE: Got {projected_score_range}. Check logic.")

if __name__ == "__main__":
    test_first_ball_projection()
