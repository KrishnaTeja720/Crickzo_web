import MySQLdb
import config

def check_data():
    try:
        db = MySQLdb.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            passwd=config.MYSQL_PASSWORD,
            db=config.MYSQL_DB
        )
        cur = db.cursor()
        
        print("Checking All Matches:")
        cur.execute("SELECT id, team_a, team_b, status, user_id, current_innings FROM matches ORDER BY id DESC LIMIT 5")
        for row in cur.fetchall():
            print(row)
            
        print("\nChecking Users:")
        cur.execute("SELECT id, email, username FROM users")
        for row in cur.fetchall():
            print(row)
            
        db.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_data()
