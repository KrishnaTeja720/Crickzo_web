from db import mysql
from flask import Flask
import config

app = Flask(__name__)
app.config.from_object(config)
mysql.init_app(app)

def debug_balls(match_id, innings):
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute("SELECT team_a, team_b FROM matches WHERE id=%s", (match_id,))
        match = cur.fetchone()
        print(f"Match {match_id}: {match[0]} vs {match[1]}")
        
        cur.execute("SELECT over_number, ball_number, runs, extras, extras_type, wicket FROM ball_by_ball WHERE match_id=%s AND innings=%s ORDER BY id ASC", (match_id, innings))
        rows = cur.fetchall()
        for r in rows:
            print(f"O{r[0]} B{r[1]}: {r[2]}R + {r[3]}E ({r[4]}), W={r[5]}")
            
        cur.execute("SELECT striker, non_striker, bowler FROM current_players WHERE match_id=%s", (match_id,))
        cp = cur.fetchone()
        print(f"Current Players: Striker={cp[0]}, Non-Striker={cp[1]}, Bowler={cp[2]}")

if __name__ == "__main__":
    debug_balls(159, 2)
