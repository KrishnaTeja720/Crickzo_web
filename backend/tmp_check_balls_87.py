
from db import mysql
from app import app

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, batsman, bowler, runs, extras, wicket, extras_type FROM ball_by_ball WHERE match_id=87")
    balls = cur.fetchall()
    for b in balls:
        print(b)
