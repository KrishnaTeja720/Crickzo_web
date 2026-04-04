from app import app
from db import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SELECT m.id, m.team_a, m.team_b, s.runs, s.wickets, s.overs FROM matches m JOIN match_scores s ON m.id = s.match_id WHERE s.runs > 0 ORDER BY m.id DESC")
    print("ACTIVE MATCHES:", cur.fetchall())
