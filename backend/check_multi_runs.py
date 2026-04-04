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
    cur.execute("SELECT runs, extras, extras_type FROM ball_by_ball WHERE extras_type IS NOT NULL")
    results = cur.fetchall()
    print(f"TOTAL EXTRA BALLS: {len(results)}")
    multi = [r for r in results if r[1] > 1 or (r[2] in ['bye', 'legbye'] and r[1] > 0)]
    print(f"MULTI-RUN EXTRAS (extras > 1 or non-zero bye/legbye): {len(multi)}")
    for m in multi[:10]:
        print(m)
