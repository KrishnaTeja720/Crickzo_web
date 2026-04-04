import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
import config
import MySQLdb

try:
    conn = MySQLdb.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        passwd=config.MYSQL_PASSWORD,
        db=config.MYSQL_DB
    )
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("Tables in database:", [t[0] for t in tables])
    cursor.close()
    conn.close()
    print("Database connection successful.")
except Exception as e:
    print(f"Database connection failed: {e}")
