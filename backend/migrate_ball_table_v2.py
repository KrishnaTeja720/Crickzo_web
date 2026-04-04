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
    try:
        cur.execute("ALTER TABLE ball_by_ball ADD COLUMN extras_type VARCHAR(20)")
    except: pass
    try:
        cur.execute("ALTER TABLE ball_by_ball ADD COLUMN extras_runs INT")
    except: pass
    mysql.connection.commit()
    print("Migration complete: added extras_type and extras_runs to ball_by_ball")
