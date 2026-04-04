import mysql.connector

def populate_players():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="crickai_db"
        )
        cur = conn.cursor()
        
        # Check if vishnu team has players
        cur.execute("SELECT * FROM players WHERE team_name='vishnu'")
        if not cur.fetchone():
            print("Populating players for team 'vishnu'...")
            players = [
                ('Player1', 'vishnu'),
                ('Player2', 'vishnu'),
                ('Player3', 'vishnu'),
                ('Player4', 'vishnu'),
                ('Player5', 'vishnu')
            ]
            cur.executemany("INSERT INTO players (player_name, team_name) VALUES (%s, %s)", players)
            conn.commit()
            print("Players populated successfully.")
        else:
            print("Players already exist for team 'vishnu'.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error populating players: {e}")

if __name__ == "__main__":
    populate_players()
