from app import app
from db import mysql

def debug_players():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        # Check match 71 teams
        cur.execute("SELECT team_a, team_b FROM matches WHERE id=71")
        match = cur.fetchone()
        print(f"Match 71 Teams: '{match[0]}', '{match[1]}'")
        
        # Check players in match_players for 71
        cur.execute("SELECT player_name, team_name FROM match_players WHERE match_id=71")
        mp = cur.fetchall()
        print(f"Match Players for 71: {mp}")
        
        # Check global players
        cur.execute("SELECT player_name, team_name FROM players")
        p = cur.fetchall()
        print(f"Global Players: {p}")
        
        cur.close()

if __name__ == "__main__":
    debug_players()
