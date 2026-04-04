from db import mysql
from flask import Flask
import config

app = Flask(__name__)
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
mysql.init_app(app)

def debug():
    with app.app_context():
        cur = mysql.connection.cursor()
        print("--- USERS ---")
        cur.execute("SELECT id, name, email FROM users")
        users = cur.fetchall()
        for u in users:
            print(f"USER_ID: {u[0]}, Name: {u[1]}, Email: {u[2]}")
            
        print("\n--- MATCHES ---")
        cur.execute("SELECT id, user_id, team_a, team_b, status FROM matches")
        matches = cur.fetchall()
        for m in matches:
            print(f"MATCH_ID: {m[0]}, OWNER_ID: {m[1]}, Team A: {m[2]}, Team B: {m[3]}, Status: {m[4]}")

if __name__ == "__main__":
    debug()
