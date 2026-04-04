import mysql.connector
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

try:
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )
    cur = conn.cursor()
    
    print(f"Connecting to {MYSQL_DB}...")
    
    # Add total_balls to match_scores
    cur.execute("SHOW COLUMNS FROM match_scores LIKE 'total_balls'")
    if not cur.fetchone():
        print("Adding total_balls to match_scores...")
        cur.execute("ALTER TABLE match_scores ADD COLUMN total_balls INT DEFAULT 0")
        conn.commit()
    else:
        print("total_balls already exists in match_scores.")

    # Add balls to bowler_stats if not exists (to track legal balls)
    cur.execute("SHOW COLUMNS FROM bowler_stats LIKE 'balls'")
    if not cur.fetchone():
        print("Adding balls to bowler_stats...")
        cur.execute("ALTER TABLE bowler_stats ADD COLUMN balls INT DEFAULT 0")
        conn.commit()

    conn.close()
    print("Migration completed successfully!")
except Exception as e:
    print(f"Migration failed: {e}")
