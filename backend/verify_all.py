from app import app
from db import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, team_a, team_b, status FROM matches WHERE id >= 140")
    rows = cur.fetchall()
    for r in rows:
        print(f"ID {r[0]}: {r[1]} vs {r[2]} ({r[3]})")
