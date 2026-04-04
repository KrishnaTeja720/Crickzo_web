from flask_mysqldb import MySQL
from flask import Flask
import os

app = Flask(__name__)
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'crickai_db'
mysql = MySQL(app)

with app.app_context():
    cur = mysql.connection.cursor()
    # Search for CSE vs ECE match
    cur.execute("SELECT id, team_a, team_b FROM matches WHERE (team_a LIKE '%CSE%' AND team_b LIKE '%ECE%') OR (team_a LIKE '%ECE%' AND team_b LIKE '%CSE%') ORDER BY id DESC LIMIT 1")
    match = cur.fetchone()
    
    if match:
        m_id, t_a, t_b = match
        print(f"Match Found: ID {m_id} ({t_a} vs {t_b})")
        print("-" * 30)
        
        cur.execute("SELECT player_id, player_name, team_name, role FROM match_players WHERE match_id = %s ORDER BY team_name", (m_id,))
        players = cur.fetchall()
        
        for p in players:
            p_id, name, team, role = p
            print(f"[{team}] ID: {p_id} | Name: {name} | Role: {role}")
    else:
        print("No match found for CSE vs ECE.")
