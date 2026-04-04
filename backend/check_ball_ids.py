from db import mysql
from flask import Flask
import config

app = Flask(__name__)
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
app.config['MYSQL_PORT'] = 3306
mysql.init_app(app)

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, runs, extras, extras_type FROM ball_by_ball ORDER BY id DESC LIMIT 10")
    results = cur.fetchall()
    print("ID | RUNS | EXTRAS | TYPE")
    print("-" * 30)
    for r in results:
        print(f"{r[0]:>2} | {r[1]:>4} | {r[2]:>6} | {r[3]}")
