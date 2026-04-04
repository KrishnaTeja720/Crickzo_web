from app import app
from db import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM match_players WHERE match_id=100")
    print(cur.fetchone())
