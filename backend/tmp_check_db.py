from db import mysql
from flask import Flask
import config

app = Flask(__name__)
app.config.from_object(config)
mysql.init_app(app)

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, team_a, team_b, status, user_id FROM matches")
    rows = cur.fetchall()
    print("MATCHES IN DB:")
    for r in rows:
        print(r)
    
    cur.execute("SELECT id, name FROM users")
    users = cur.fetchall()
    print("\nUSERS IN DB:")
    for u in users:
        print(u)
