import requests

url = "http://127.0.0.1:5005"
user_id = 1

def check_status(mid):
    res = requests.get(f"{url}/match/state/{mid}?user_id={user_id}")
    # We need to check matches table status too, but match/state doesn't return status 'live'/'upcoming' directly to UI usually?
    # Actually match/state should return it.
    # Let's check routes.py match_state again.
    return res.json()

# 1. Create match
payload = {
    "user_id": user_id,
    "team_a": "TestA",
    "team_b": "TestB",
    "format": "20",
    "venue": "Test Venue",
    "toss": "Team A",
    "toss_decision": "Batting",
    "pitch": "Batting",
    "weather": "Clear"
}

res = requests.post(f"{url}/match/create", json=payload)
data = res.json()
mid = data['match_id']
print(f"CREATED MATCH {mid}")

# Check status in DB
import MySQLdb
import config
db=MySQLdb.connect(host=config.MYSQL_HOST, user=config.MYSQL_USER, passwd=config.MYSQL_PASSWORD, db=config.MYSQL_DB)
cur=db.cursor()

def get_db_status(mid):
    cur.execute("SELECT status FROM matches WHERE id=%s", (mid,))
    return cur.fetchone()[0]

print(f"INITIAL DB STATUS: {get_db_status(mid)}")

# 2. Call match/state (frontend does this on Scoring page)
requests.get(f"{url}/match/state/{mid}?user_id={user_id}")
print(f"DB STATUS AFTER match/state: {get_db_status(mid)}")

# 3. Call match/start (frontend does this when Start Match is clicked)
start_payload = {
    "match_id": mid,
    "striker": "P1",
    "non_striker": "P2",
    "bowler": "B1"
}
requests.post(f"{url}/match/start", json=start_payload)
print(f"DB STATUS AFTER match/start: {get_db_status(mid)}")

# 4. Call ball submission
ball_payload = {
    "match_id": mid,
    "runs": 1,
    "is_wicket": False
}
requests.post(f"{url}/match/ball", json=ball_payload)
print(f"DB STATUS AFTER match/ball (1 run): {get_db_status(mid)}")
