from app import app
from db import mysql

def debug_match_70():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        # Match info
        cur.execute("SELECT id, user_id, team_a, team_b FROM matches WHERE id=70")
        match = cur.fetchone()
        print(f"Match 70: {match}")
        
        # Players in match_players for 70
        cur.execute("SELECT player_name, team_name FROM match_players WHERE match_id=70")
        mp = cur.fetchall()
        print(f"Match Players for 70: {mp}")
        
        # Global players for rcb and csk
        cur.execute("SELECT player_name, team_name FROM players WHERE team_name IN ('rcb', 'csk')")
        p = cur.fetchall()
        print(f"Global Players for RCB/CSK: {p}")
        
        cur.close()

if __name__ == "__main__":
    debug_match_70()
