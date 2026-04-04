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
        
        # Check if column exists
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
