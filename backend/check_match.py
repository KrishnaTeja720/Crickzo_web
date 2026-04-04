from app import app
from db import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, user_id, team_a, team_b FROM matches WHERE id=57")
    row = cur.fetchone()
    print(f"Match 57: {row}")
    
    cur.execute("SELECT * FROM current_players WHERE match_id=57")
    cp = cur.fetchone()
    print(f"Current Players: {cp}")
