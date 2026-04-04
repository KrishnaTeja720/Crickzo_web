from app import app
from db import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, batsman, bowler, runs, extras FROM ball_by_ball WHERE match_id=96")
    print(cur.fetchall())
