import requests
import time

BASE_URL = "http://localhost:5000" # Assuming backend is running locally

def test_undo_logic():
    print("Starting Undo Logic Verification...")
    
    # 1. Create a match
    match_data = {
        "user_id": 1,
        "team_a": "Team Alpha",
        "team_b": "Team Beta",
        "format": "T20",
        "venue": "Test Ground",
        "toss": "Team Alpha",
        "toss_decision": "Batting",
        "pitch": "Flat",
        "weather": "Sunny"
    }
    
    try:
        res = requests.post(f"{BASE_URL}/match/create", json=match_data)
        if res.status_code != 200:
            print(f"Failed to create match: {res.text}")
            return
        
        match_id = res.json().get("match_id")
        print(f"Created match with ID: {match_id}")
        
        # 2. Setup match (players)
        setup_data = {
            "match_id": match_id,
            "team_a_players": ["A1", "A2", "A3"],
            "team_b_players": ["B1", "B2", "B3"]
        }
        requests.post(f"{BASE_URL}/match/setup", json=setup_data)
        
        # 3. Balls simulation
        balls = [
            {"runs": 1, "extras": 0, "wicket": 0, "batsman": "A1", "bowler": "B1"}, # 0.1
            {"runs": 4, "extras": 0, "wicket": 0, "batsman": "A1", "bowler": "B1"}, # 0.2
            {"runs": 0, "extras": 1, "extra_type": "wide", "wicket": 0, "batsman": "A1", "bowler": "B1"}, # 0.2 (wide)
            {"runs": 0, "extras": 0, "wicket": 1, "batsman": "A1", "bowler": "B1"}  # 0.3
        ]
        
        for i, b in enumerate(balls):
            b["match_id"] = match_id
            b["innings"] = 1
            requests.post(f"{BASE_URL}/match/ball", json=b)
            print(f"Submitted ball {i+1}")
            
        # Check score before undo
        res = requests.get(f"{BASE_URL}/match/state/{match_id}?innings=1")
        state = res.json()
        print(f"Score before undo: {state['runs']}/{state['wickets']} in {state['overs']} overs (Balls: {state['balls']})")
        
        # Expected: 1+4+0+1(wide) = 6 runs, 1 wicket, 0.3 overs (3 legal balls)
        if state['balls'] != 3 or state['overs'] != "0.3":
            print(f"ERROR: Expected 0.3 overs, got {state['overs']}")
            
        # 4. Undo last ball (wicket)
        print("Undoing last ball...")
        requests.delete(f"{BASE_URL}/match/undo/{match_id}")
        
        res = requests.get(f"{BASE_URL}/match/state/{match_id}?innings=1")
        state = res.json()
        print(f"Score after undo: {state['runs']}/{state['wickets']} in {state['overs']} overs (Balls: {state['balls']})")
        
        # Expected: 6 runs, 0 wickets, 0.2 overs
        if state['wickets'] == 0 and state['overs'] == "0.2" and state['balls'] == 2:
            print("SUCCESS: Undo logic verified!")
        else:
            print(f"FAILURE: Expected 6/0 in 0.2, got {state['runs']}/{state['wickets']} in {state['overs']}")
            
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    # Note: This script requires the backend to be running.
    # Since I cannot run the backend server myself, I'll provide this for the user.
    test_undo_logic()
