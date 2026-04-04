import MySQLdb
import config

def migrate():
    try:
        db = MySQLdb.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            passwd=config.MYSQL_PASSWORD,
            db=config.MYSQL_DB
        )
        cur = db.cursor()
        
        # Check if status column exists
        cur.execute("SHOW COLUMNS FROM batsman_stats LIKE 'status'")
        if not cur.fetchone():
            print("Adding 'status' column to batsman_stats...")
            cur.execute("ALTER TABLE batsman_stats ADD COLUMN status VARCHAR(255) DEFAULT 'not out'")
            print("Successfully added 'status' column.")
        else:
            print("'status' column already exists.")
            
        db.commit()
        db.close()
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
