from flask import Flask
from db import mysql
import config

app = Flask(__name__)
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
mysql.init_app(app)

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, team_a, team_b, format FROM matches WHERE team_a='VerifyA' ORDER BY id DESC LIMIT 1")
    match = cur.fetchone()
    if match:
        print(f"Match ID: {match[0]}, TeamA: {match[1]}, TeamB: {match[2]}, Format: {match[3]}")
    else:
        print("Match not found!")
