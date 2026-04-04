import MySQLdb
import config

def check_players():
    try:
        db = MySQLdb.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            passwd=config.MYSQL_PASSWORD,
            db=config.MYSQL_DB
        )
        cur = db.cursor()
        
        print("Checking Current Players for Match 150:")
        cur.execute("SELECT * FROM current_players WHERE match_id=150")
        for row in cur.fetchall():
            print(row)
            
        print("\nChecking Match State for Match 150:")
        cur.execute("SELECT status, current_innings, user_id FROM matches WHERE id=150")
        print(cur.fetchone())
        
        db.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_players()
