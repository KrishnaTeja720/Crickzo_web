from app import app
from db import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, team_a, team_b FROM matches")
    print("MATCHES:", cur.fetchall())
