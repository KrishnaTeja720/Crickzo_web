
from db import mysql
from app import app

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("DESCRIBE match_scores")
    schema = cur.fetchall()
    for col in schema:
        print(col)
