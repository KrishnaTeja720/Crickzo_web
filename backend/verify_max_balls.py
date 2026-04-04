from flask import Flask
from db import mysql
import config
import routes

app = Flask(__name__)
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
mysql.init_app(app)

def check_max_balls(match_id):
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute("SELECT format FROM matches WHERE id=%s", (match_id,))
        match_format = cur.fetchone()[0]
        
        # Manually run the logic I added to routes.py to verify
        try:
            max_balls = int(match_format) * 6
            print(f"Match format: {match_format}")
            print(f"Calculated max_balls: {max_balls}")
            if max_balls == 36:
                print("LOGIC SUCCESS: max_balls is 36 for 6 overs.")
            else:
                print(f"LOGIC FAILURE: Expected 36, got {max_balls}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_max_balls(103) # Use the match ID I just created
