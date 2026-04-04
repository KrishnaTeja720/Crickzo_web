import os
from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'crickai_db'

mysql = MySQL(app)

with app.app_context():
    cur = mysql.connection.cursor()
    
    match_id = 69
    print(f"--- CHECK FOR MATCH {match_id} ---")
    cur.execute("SELECT id, team_a, team_b, status FROM matches WHERE id=%s", (match_id,))
    r = cur.fetchone()
    if r:
        print(f"Match ID: {r[0]}, Teams: '{r[1]}' vs '{r[2]}', Status: {r[3]}")
    else:
        print(f"Match {match_id} NOT FOUND.")

    # Check for players for the latest 3 matches to see if they are going to the wrong ID
    print("\n--- ALL PLAYERS from latest 3 matches ---")
    cur.execute("SELECT id, match_id, player_name, team_name FROM match_players ORDER BY id DESC LIMIT 20")
    for r in cur.fetchall():
        print(f"ID={r[0]}, Match={r[1]}, Player='{r[2]}', Team='{r[3]}'")
