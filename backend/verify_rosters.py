from app import app
from db import mysql

def verify_rcb_csk():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        cur.execute("SELECT player_name, team_name FROM players WHERE team_name IN ('rcb', 'csk')")
        p = cur.fetchall()
        print(f"Global Players for RCB/CSK: {p}")
        
        cur.close()

if __name__ == "__main__":
    verify_rcb_csk()
