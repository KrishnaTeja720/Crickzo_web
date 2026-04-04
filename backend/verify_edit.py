import requests
import json

base_url = "http://localhost:5001"

print("1. Creating Match...")
res = requests.post(f"{base_url}/match/create", json={
    "user_id": 1,
    "team_a": "India",
    "team_b": "Australia",
    "format": "T20",
    "venue": "Test Stadium",
    "toss": "India",
    "pitch": "Dry",
    "weather": "Clear"
})
match_id = res.json()["match_id"]
print(f"Match created: {match_id}")

print("2. Starting Match...")
res = requests.post(f"{base_url}/match/start", json={
    "match_id": match_id,
    "striker": "Rohit",
    "non_striker": "Virat",
    "bowler": "Starc"
})
print("Start output:", res.json())

print("3. Recording a ball (4 runs)...")
res = requests.post(f"{base_url}/match/ball", json={
    "match_id": match_id,
    "innings": 1,
    "runs": 4,
    "extra_type": None,
    "is_wicket": False,
    "batsman": "Rohit",
    "bowler": "Starc"
})
print("Ball output:", res.json())

print("4. Checking Score...")
res = requests.get(f"{base_url}/match/state/{match_id}?user_id=1")
print("Score:", {k: res.json()[k] for k in ["runs", "wickets", "overs"]})

print("5. Editing Score manually to 15/1 in 2.0 overs...")
res = requests.post(f"{base_url}/match/edit_score", json={
    "match_id": match_id,
    "innings": 1,
    "runs": 15,
    "wickets": 1,
    "overs": "2.0"
})
print("Edit output:", res.json())

print("6. Checking Score after edit...")
res = requests.get(f"{base_url}/match/state/{match_id}?user_id=1")
print("Score after edit:", {k: res.json()[k] for k in ["runs", "wickets", "overs"]})

print("7. Checking Prediction data...")
res = requests.get(f"{base_url}/match/predictions/{match_id}")
print("Prediction data keys:", res.json())

print("8. Recording another ball (1 run)")
res = requests.post(f"{base_url}/match/ball", json={
    "match_id": match_id,
    "innings": 1,
    "runs": 1,
    "extra_type": None,
    "is_wicket": False,
    "batsman": "Rohit",
    "bowler": "Starc"
})
print("Ball output:", res.json())

print("9. Checking Score after another ball (should be 16/1, 2.1 overs)...")
res = requests.get(f"{base_url}/match/state/{match_id}?user_id=1")
print("Score after ball:", {k: res.json()[k] for k in ["runs", "wickets", "overs"]})

print("10. Refreshing score...")
res = requests.post(f"{base_url}/match/refresh_score", json={
    "match_id": match_id,
    "innings": 1
})
print("Refresh output:", res.json())

print("11. Checking score after refresh (should be 5/0, 0.2 overs or similar)...")
res = requests.get(f"{base_url}/match/state/{match_id}?user_id=1")
print("Score after refresh:", {k: res.json()[k] for k in ["runs", "wickets", "overs"]})

