from app import app
from db import mysql

def seed_common_teams():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        common_teams = {
            'rcb': ['Virat Kohli', 'Faf du Plessis', 'Maxwell', 'Siraj', 'Dinesh Karthik', 'Green', 'Patidar'],
            'csk': ['MS Dhoni', 'Ruturaj Gaikwad', 'Ravindra Jadeja', 'Shivam Dube', 'Deepak Chahar', 'Rahane', 'Mitchell'],
            'mi': ['Rohit Sharma', 'Hardik Pandya', 'Suryakumar Yadav', 'Bumrah', 'Ishan Kishan', 'Tim David', 'Tilak Varma']
        }
        
        for team, players in common_teams.items():
            print(f"Checking players for team '{team}'...")
            cur.execute("SELECT player_name FROM players WHERE team_name=%s", (team,))
            existing = [row[0] for row in cur.fetchall()]
            
            for player in players:
                if player not in existing:
                    print(f"Adding player '{player}' to team '{team}'")
                    cur.execute("INSERT INTO players (player_name, team_name) VALUES (%s, %s)", (player, team))
        
        mysql.connection.commit()
        print("Common teams seeded successfully.")
        cur.close()

if __name__ == "__main__":
    seed_common_teams()
