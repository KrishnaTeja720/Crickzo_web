from app import app
from db import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    print("Adding current_innings to matches table...")
    try:
        cur.execute("ALTER TABLE matches ADD COLUMN current_innings INT DEFAULT 1")
        mysql.connection.commit()
        print("Success!")
    except Exception as e:
        print(f"Error or already exists: {e}")
