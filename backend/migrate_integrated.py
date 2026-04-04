from app import app
from db import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    
    print("Connecting to DB using Flask Context...")
    
    # Add total_balls to match_scores
    cur.execute("SHOW COLUMNS FROM match_scores LIKE 'total_balls'")
    if not cur.fetchone():
        print("Adding total_balls to match_scores...")
        cur.execute("ALTER TABLE match_scores ADD COLUMN total_balls INT DEFAULT 0")
        mysql.connection.commit()
    else:
        print("total_balls already exists in match_scores.")

    # Add balls to bowler_stats if not exists
    cur.execute("SHOW COLUMNS FROM bowler_stats LIKE 'balls'")
    if not cur.fetchone():
        print("Adding balls to bowler_stats...")
        cur.execute("ALTER TABLE bowler_stats ADD COLUMN balls INT DEFAULT 0")
        mysql.connection.commit()

    print("Migration completed successfully!")
