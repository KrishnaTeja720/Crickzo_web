from app import app
from db import mysql

def seed():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        # Check if vishnu team has players
        cur.execute("SELECT * FROM players WHERE team_name='vishnu'")
        if not cur.fetchone():
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
            print("Players seeded successfully.")
        else:
            print("Players already exist for team 'vishnu'.")
        cur.close()

if __name__ == "__main__":
    seed()
