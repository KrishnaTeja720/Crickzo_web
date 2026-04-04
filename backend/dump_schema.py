import os
from flask import Flask
from flask_mysqldb import MySQL
import config

app = Flask(__name__)
app.config.update({
    'MYSQL_HOST': config.MYSQL_HOST,
    'MYSQL_USER': config.MYSQL_USER,
    'MYSQL_PASSWORD': config.MYSQL_PASSWORD,
    'MYSQL_DB': config.MYSQL_DB
})
mysql = MySQL(app)

def dump_schema():
    with app.app_context():
        cur = mysql.connection.cursor()
        tables = ['matches', 'ball_by_ball', 'match_scores', 'match_players']
        for table in tables:
            print(f"\n--- Schema for {table} ---")
            cur.execute(f"DESC {table}")
            for col in cur.fetchall():
                print(col)

if __name__ == "__main__":
    dump_schema()
