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
    cur.execute("SELECT COUNT(*) FROM ball_by_ball WHERE runs IS NULL OR extras IS NULL")
    null_count = cur.fetchone()[0]
    print(f"NULL COUNT: {null_count}")
    
    cur.execute("SELECT runs, extras FROM ball_by_ball ORDER BY id DESC LIMIT 5")
    print("LATEST BALLS (runs, extras):")
    for r in cur.fetchall():
        print(r)
