import MySQLdb
import config

try:
    db = MySQLdb.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        passwd=config.MYSQL_PASSWORD,
        db=config.MYSQL_DB
    )
    cur = db.cursor()
    cur.execute("SELECT id, team_a, team_b, status FROM matches")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    db.close()
except Exception as e:
    print(f"Error: {e}")
