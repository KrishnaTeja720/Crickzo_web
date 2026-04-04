import requests

match_id = 113
url = f"http://127.0.0.1:5005/match/scorecard/{match_id}"

try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("API RESPONSE SUCCESS")
        print(f"Team A Batting Count: {len(data['team_a']['batting'])}")
        print(f"Team B Batting Count: {len(data['team_b']['batting'])}")
        if len(data['team_a']['batting']) > 0:
            print(f"Sample Status: {data['team_a']['batting'][0].get('status', 'MISSING')}")
    else:
        print(f"API FAILED: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"ERROR: {e}")
