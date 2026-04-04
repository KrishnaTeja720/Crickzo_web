from db import mysql
from app import app
import config

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SELECT team_a, team_b, current_innings FROM matches WHERE id=57")
    match = cur.fetchone()
    print(f"Match 57 Teams: {match}")
    
    cur.execute("SELECT COUNT(*) FROM match_players WHERE match_id=57")
    print(f"Match Players Count: {cur.fetchone()[0]}")
    
    if match:
        team_a, team_b, innings = match
        cur.execute("SELECT COUNT(*) FROM players WHERE team_name=%s", (team_a,))
        print(f"Players in global roster for {team_a}: {cur.fetchone()[0]}")
        cur.execute("SELECT COUNT(*) FROM players WHERE team_name=%s", (team_b,))
        print(f"Players in global roster for {team_b}: {cur.fetchone()[0]}")
    
    cur.close()
