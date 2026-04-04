import requests
import json

# Try to find a live match ID
match_id = 90  # I'll try a few or ask user

url = f"http://localhost:5000/match/state/{match_id}?innings=2"

try:
    r = requests.get(url)
    print(f"Status: {r.status_code}")
    data = r.json()
    print("\nAPI RESPONSE:")
    print(json.dumps(data, indent=2))
    
    runs = data.get("runs")
    balls = data.get("total_balls", data.get("balls"))
    overs = data.get("overs")
    crr = data.get("crr")
    
    print(f"\nEXTRACTED:")
    print(f"  Runs: {runs}")
    print(f"  Balls: {balls}")
    print(f"  Overs: {overs}")
    print(f"  CRR: {crr}")
    
except Exception as e:
    print(f"Error: {e}")
