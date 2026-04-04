import os
from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config.update({
    'MYSQL_HOST': 'localhost',
    'MYSQL_USER': 'root',
    'MYSQL_PASSWORD': '',
    'MYSQL_DB': 'crickai_db'
})
mysql = MySQL(app)

def check_match():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        match_id = 153
        print(f"\n--- MATCH {match_id} DIAGNOSTIC ---")
        
        # Match info
        cur.execute("SELECT team_a, team_b, format FROM matches WHERE id=%s", (match_id,))
        m = cur.fetchone()
        print(f"Match Info: {m}")
        
        # Match Players (Bowlers)
        print("\nBowler Stats from match_players:")
        cur.execute("""
            SELECT player_name, team_name, bowl_overs, bowl_balls, bowl_runs_conceded, bowl_wickets 
            FROM match_players 
            WHERE match_id=%s AND (bowl_balls > 0 OR bowl_runs_conceded > 0)
        """, (match_id,))
        rows = cur.fetchall()
        for r in rows:
            print(r)
            
        # Ball by Ball count
        cur.execute("SELECT COUNT(*) FROM ball_by_ball WHERE match_id=%s", (match_id,))
        print(f"\nTotal balls in ball_by_ball: {cur.fetchone()[0]}")
        
        # Innings breakdown
        cur.execute("SELECT innings, COUNT(*) FROM ball_by_ball WHERE match_id=%s GROUP BY innings", (match_id,))
        print(f"Balls per innings: {cur.fetchall()}")
        
        # Match Scores
        cur.execute("SELECT innings, runs, wickets, overs, total_balls FROM match_scores WHERE match_id=%s", (match_id,))
        print(f"\nScoreboard summary (match_scores):")
        for r in cur.fetchall():
            print(r)

if __name__ == "__main__":
    check_match()
