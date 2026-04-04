import requests

match_id = 112
url = f"http://127.0.0.1:5005/match/scorecard/{match_id}"

try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("API RESPONSE SUCCESS")
        print(f"Team A (Mumbai) Batting Count: {len(data['team_a']['batting'])}")
        print(f"Team B (Chennai) Batting Count: {len(data['team_b']['batting'])}")
        
        print("\nTeam A Batters:", [p['player_name'] for p in data['team_a']['batting']])
        print("Team B Batters:", [p['player_name'] for p in data['team_b']['batting']])
    else:
        print(f"API FAILED: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"ERROR: {e}")
