from db import mysql
from flask import Flask
import config
import json

app = Flask(__name__)
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
mysql.init_app(app)

def list_matches():
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, team_a, team_b, status FROM matches ORDER BY id DESC LIMIT 20")
        matches = cur.fetchall()
        print("LIVE MATCHES:")
        cur.execute("SELECT id, team_a, team_b, status FROM matches WHERE status='live'")
        matches = cur.fetchall()
        for m in matches:
            print(f"ID: {m[0]}, Team A: {m[1]}, Team B: {m[2]}, Status: {m[3]}")
            
        # Check if players table has dc/gt
        cur.execute("SELECT count(*), team_name FROM players GROUP BY team_name")
        print("\nPLAYER ROSTER COUNTS:")
        for c in cur.fetchall():
            print(f"{c[1]}: {c[0]}")

if __name__ == "__main__":
    list_matches()
