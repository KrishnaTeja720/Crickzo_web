from app import app
from db import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SELECT match_id, striker, non_striker, bowler FROM current_players WHERE match_id=97")
    print(cur.fetchall())
