from app import app
from db import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute('SELECT innings, runs, balls, crr FROM match_scores WHERE match_id=88')
    res = cur.fetchall()
    print(res)
    
    cur.execute('SELECT current_innings FROM matches WHERE id=88')
    match_res = cur.fetchone()
    print("CURRENT_INNINGS:", match_res)
