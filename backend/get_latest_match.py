from app import app
from db import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM matches WHERE status='live' ORDER BY id DESC LIMIT 1")
    print(cur.fetchone())
