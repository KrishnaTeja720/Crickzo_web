import MySQLdb
import config

def migrate():
    try:
        conn = MySQLdb.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            passwd=config.MYSQL_PASSWORD,
            db=config.MYSQL_DB
        )
        cur = conn.cursor()
        
        # 1. Check bowler_stats for 'balls' column
        cur.execute("SHOW COLUMNS FROM bowler_stats LIKE 'balls'")
        if not cur.fetchone():
            print("Adding 'balls' column to 'bowler_stats'...")
            cur.execute("ALTER TABLE bowler_stats ADD COLUMN balls INT DEFAULT 0 AFTER overs")
        else:
            print("'balls' column already exists in 'bowler_stats'.")

        # 2. Check match_scores for 'balls' column (just in case, though migrate_balls.py should have handled it)
        cur.execute("SHOW COLUMNS FROM match_scores LIKE 'balls'")
        if not cur.fetchone():
            print("Adding 'balls' column to 'match_scores'...")
            cur.execute("ALTER TABLE match_scores ADD COLUMN balls INT DEFAULT 0 AFTER overs")
            
        conn.commit()
        cur.close()
        conn.close()
        print("Migration successful.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
