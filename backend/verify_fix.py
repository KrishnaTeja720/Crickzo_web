from db import mysql
from flask import Flask
import config

app = Flask(__name__)
app.config.from_object(config)
mysql.init_app(app)

with app.app_context():
    cur = mysql.connection.cursor()
    # Check Match 159
    cur.execute("SELECT id, team_a, team_b, current_innings, status FROM matches WHERE id=159")
    m = cur.fetchone()
    print(f"MATCH 159: {m}")
    
    cur.execute("SELECT innings, runs, wickets, overs, balls FROM match_scores WHERE match_id=159")
    scores = cur.fetchall()
    print("\nSCORES FOR 159:")
    for s in scores:
        print(s)
        
    cur.execute("SELECT innings, COUNT(*) FROM ball_by_ball WHERE match_id=159 GROUP BY innings")
    balls = cur.fetchall()
    print("\nBALLS FOR 159:")
    for b in balls:
        print(b)
