from app import app
from db import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SELECT match_id, runs, wickets, overs FROM match_scores WHERE runs > 0")
    print("SCORED MATCHES:", cur.fetchall())
