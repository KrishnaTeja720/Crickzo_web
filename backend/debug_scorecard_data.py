from flask import Flask
from db import mysql
import config
import json

app = Flask(__name__)
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
mysql.init_app(app)

def debug_scorecard():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        # Check global players for dc and gt
        for team in ['dc', 'gt']:
            cur.execute("SELECT count(*) FROM players WHERE team_name=%s", (team,))
            count = cur.fetchone()[0]
            print(f"DEBUG: Team '{team}' has {count} global players")
            if count < 11:
                print(f"DEBUG: Seeding 11 players for team '{team}'")
                players = [(f"{team.upper()} Player {i}", team) for i in range(1, 12)]
                cur.executemany("INSERT INTO players (player_name, team_name) VALUES (%s, %s)", players)
                mysql.connection.commit()
        
        # Check match_players for ALL matches to see if anyone has players
        cur.execute("SELECT count(*), match_id FROM match_players GROUP BY match_id")
        counts = cur.fetchall()
        print(f"DEBUG: Matches with registered players: {counts}")
        
        if match_id:
            cur.execute("SELECT * FROM match_players WHERE match_id=%s", (match_id,))
            print(f"DEBUG: Raw match_players for {match_id}: {cur.fetchall()}")
        
        # Check batsman_stats
        cur.execute("SELECT player_name, runs FROM batsman_stats WHERE match_id=%s", (match_id,))
        b_stats = cur.fetchall()
        print(f"DEBUG: Batsman Stats count: {len(b_stats)}")
        
        # Check bowler_stats
        cur.execute("SELECT player_name, runs FROM bowler_stats WHERE match_id=%s", (match_id,))
        bo_stats = cur.fetchall()
        print(f"DEBUG: Bowler Stats count: {len(bo_stats)}")

if __name__ == "__main__":
    debug_scorecard()
