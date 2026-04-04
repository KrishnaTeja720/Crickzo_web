import os
from flask import Flask
from db import mysql
from routes import rebuild_match_state
import config

app = Flask(__name__)
app.config.update({
    'MYSQL_HOST': config.MYSQL_HOST,
    'MYSQL_USER': config.MYSQL_USER,
    'MYSQL_PASSWORD': config.MYSQL_PASSWORD,
    'MYSQL_DB': config.MYSQL_DB
})
mysql.init_app(app)

def trigger():
    with app.app_context():
        match_id = 153
        print(f"Triggering rebuild for Match {match_id}...")
        rebuild_match_state(match_id)
        print("Rebuild complete!")

if __name__ == "__main__":
    trigger()
