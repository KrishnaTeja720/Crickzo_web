from app import app
from db import mysql

def trim_records():
    with app.app_context():
        cur = mysql.connection.cursor()
        print("Trimming matches table...")
        cur.execute("UPDATE matches SET team_a = TRIM(team_a), team_b = TRIM(team_b)")
        print("Trimming match_players table...")
        cur.execute("UPDATE match_players SET team_name = TRIM(team_name)")
        print("Trimming players table...")
        cur.execute("UPDATE players SET team_name = TRIM(team_name)")
        mysql.connection.commit()
        print("Trimming completed.")
        cur.close()

if __name__ == "__main__":
    trim_records()
