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

def seed_players():
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
        
        # Check latest match
        cur.execute("SELECT id, team_a, team_b FROM matches ORDER BY id DESC LIMIT 1")
        match = cur.fetchone()
        if match:
            print(f"DEBUG: Latest Match ID: {match[0]} ({match[1]} vs {match[2]})")

if __name__ == "__main__":
    seed_players()
