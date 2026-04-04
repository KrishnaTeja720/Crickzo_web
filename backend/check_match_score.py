from app import app
from db import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SELECT match_id, innings, runs, balls FROM match_scores WHERE match_id=96")
    print(cur.fetchall())
