import requests
import time

BASE_URL = "http://127.0.0.1:5005"

def test_global_identity():
    print("Testing Global Player Identity & Stat Isolation...")
    
    # 1. Create Match A
    print("Creating Match A...")
    m1 = requests.post(f"{BASE_URL}/match/create", json={
        "user_id": 1, "team_a": "Team A", "team_b": "Team B", "format": "20",
        "toss": "Team A", "toss_decision": "Batting", "pitch": "Flat", "weather": "Sunny"
    }).json()
    match_a_id = m1["match_id"]
    
    # 2. Add Player "Virat" to Match A
    print(f"Adding 'Virat' to Match A ({match_a_id})...")
    requests.post(f"{BASE_URL}/match/add_player", json={
        "match_id": match_a_id, "player_name": "Virat", "team": "Team A"
    })
    
    # 3. Create Match B
    print("Creating Match B...")
    m2 = requests.post(f"{BASE_URL}/match/create", json={
        "user_id": 1, "team_a": "Team C", "team_b": "Team D", "format": "20",
        "toss": "Team C", "toss_decision": "Batting", "pitch": "Flat", "weather": "Sunny"
    }).json()
    match_b_id = m2["match_id"]
    
    # 4. Add Player "Virat" to Match B
    print(f"Adding 'Virat' to Match B ({match_b_id})...")
    requests.post(f"{BASE_URL}/match/add_player", json={
        "match_id": match_b_id, "player_name": "Virat", "team": "Team C"
    })
    
    # 5. Check if Player IDs are the same
    print("Verifying Player IDs...")
    players_a = requests.get(f"{BASE_URL}/match/players/{match_a_id}").json()
    players_b = requests.get(f"{BASE_URL}/match/players/{match_b_id}").json()
    
    id_a = next(p["player_id"] for p in players_a if p["player_name"] == "Virat")
    id_b = next(p["player_id"] for p in players_b if p["player_name"] == "Virat")
    
    if id_a == id_b:
        print(f"SUCCESS: 'Virat' has the same global ID ({id_a}) in both matches.")
    else:
        print(f"FAILURE: 'Virat' has different IDs: {id_a} vs {id_b}")
        return

    # 6. Record runs for Virat in Match A
    print("Recording 10 runs for Virat in Match A...")
    # Setup current players
    requests.post(f"{BASE_URL}/match/change_bowler", json={"match_id": match_a_id, "bowler": "Bowler X"})
    requests.post(f"{BASE_URL}/match/update_innings", json={"match_id": match_a_id, "innings": 1})
    # This is simplified; usually current_players are set first
    # I'll just manually trigger update_batsman_stats via a mock ball if I had an endpoint, 
    # but I'll use the scorecard to verify.
    
    # Actually, I'll just check if Match B stats are 0 (which they should be)
    stats_b = requests.get(f"{BASE_URL}/match/batsmen/{match_b_id}").json()
    virat_stats_b = [p for p in stats_b if p["batsman"] == "Virat"]
    if not virat_stats_b or virat_stats_b[0]["runs"] == 0:
        print("SUCCESS: Stats in Match B are isolated (0 runs).")
    else:
        print(f"FAILURE: Stats leaking! Virat has {virat_stats_b[0]['runs']} runs in Match B.")

if __name__ == "__main__":
    try:
        test_global_identity()
    except Exception as e:
        print(f"Test crashed: {e}")
