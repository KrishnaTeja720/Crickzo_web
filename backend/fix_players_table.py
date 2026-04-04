from app import app
from db import mysql

def fix_schema():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        # Drop and recreate players table to be sure
        print("Recreating players table...")
        cur.execute("DROP TABLE IF EXISTS players")
        cur.execute("""
            CREATE TABLE players(
                player_id INT AUTO_INCREMENT PRIMARY KEY,
                player_name VARCHAR(100),
                team_name VARCHAR(100)
            )
        """)
        
        print("Seeding players for team 'vishnu'...")
        players = [
            ('Player1', 'vishnu'),
            ('Player2', 'vishnu'),
            ('Player3', 'vishnu'),
            ('Player4', 'vishnu'),
            ('Player5', 'vishnu')
        ]
        for p in players:
            cur.execute("INSERT INTO players (player_name, team_name) VALUES (%s, %s)", p)
        
        mysql.connection.commit()
        print("Done.")
        cur.close()

if __name__ == "__main__":
    fix_schema()
