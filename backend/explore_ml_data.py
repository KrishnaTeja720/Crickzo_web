import os
from flask import Flask
from flask_mysqldb import MySQL
import pandas as pd
import config

app = Flask(__name__)
app.config.update({
    'MYSQL_HOST': config.MYSQL_HOST,
    'MYSQL_USER': config.MYSQL_USER,
    'MYSQL_PASSWORD': config.MYSQL_PASSWORD,
    'MYSQL_DB': config.MYSQL_DB
})
mysql = MySQL(app)

def explore_data():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        # 1. Total matches
        cur.execute("SELECT status, COUNT(*) FROM matches GROUP BY status")
        print("\nMatch Status counts:")
        print(cur.fetchall())
        
        # 2. Sample ball_by_ball data for completed matches
        cur.execute("""
            SELECT b.match_id, b.innings, b.runs, b.extras, b.wicket, m.winner, m.team_a, m.team_b, m.format
            FROM ball_by_ball b
            JOIN matches m ON b.match_id = m.id
            WHERE m.status = 'completed'
            LIMIT 10
        """)
        print("\nSample Ball-by-Ball data for training:")
        rows = cur.fetchall()
        for r in rows:
            print(r)
            
        # 3. Check if we have enough data for a meaningful model
        cur.execute("SELECT COUNT(*) FROM ball_by_ball b JOIN matches m ON b.match_id = m.id WHERE m.status = 'completed'")
        total_balls = cur.fetchone()[0]
        print(f"\nTotal historical balls available for training: {total_balls}")

if __name__ == "__main__":
    explore_data()
