import requests
import json

BASE_URL = "http://127.0.0.1:5000"
USER_ID = 1

def test_initial_predictions():
    # 1. Create a match
    match_data = {
        "user_id": USER_ID,
        "team_a": "Initial A",
        "team_b": "Initial B",
        "format": "T20",
        "toss": "Initial A",
        "toss_decision": "Batting"
    }
    resp = requests.post(f"{BASE_URL}/match/create", json=match_data)
    match_id = resp.json().get("match_id")
    print(f"Created Match ID: {match_id}")

    # 2. Get predictions for Innings 1 (0 balls)
    resp = requests.get(f"{BASE_URL}/match/predictions/{match_id}?innings=1")
    preds = resp.json()
    print(json.dumps(preds, indent=2))

    # Assertions
    wp = preds['winner_prediction']
    assert wp['team_a'] == 50.0 and wp['team_b'] == 50.0, f"Win Prob fail: {wp}"
    
    ps = preds['projected_score']
    assert ps['range'] == "0", f"Projected Score fail: {ps}"
    
    no = preds['next_over']
    assert no['runs'] == 0, f"Next Over fail: {no}"
    
    n5 = preds['next_5_overs']
    assert n5['runs'] == 0, f"Next 5 Overs fail: {n5}"
    
    wprob = preds['wicket_probability']
    assert wprob == 50, f"Wicket Prob fail: {wprob}"
    
    bf = preds['batsman_forecast']
    for b in bf:
        assert b['final_runs'] == 0, f"Batsman Forecast fail: {b}"

    print("\nSUCCESS: All initial prediction values are correct!")

if __name__ == "__main__":
    test_initial_predictions()
