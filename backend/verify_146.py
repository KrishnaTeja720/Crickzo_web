from app import app
from db import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, team_a, team_b, status FROM matches WHERE id=146")
    row = cur.fetchone()
    print("MATCH 146:", row)
