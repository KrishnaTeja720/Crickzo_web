import MySQLdb
import config

conn = MySQLdb.connect(host=config.MYSQL_HOST, user=config.MYSQL_USER, passwd=config.MYSQL_PASSWORD, db=config.MYSQL_DB)
cur = conn.cursor()

cur.execute("DESCRIBE match_scores")
cols = cur.fetchall()
print("COLUMN ORDER:")
for i, col in enumerate(cols):
    print(f"  {i}: {col[0]} ({col[1]})")

cur.execute("SELECT id, team_a, team_b FROM matches ORDER BY id DESC LIMIT 1")
match = cur.fetchone()
if match:
    mid = match[0]
    print(f"\nDATA FOR MATCH {mid} ({match[1]} vs {match[2]}):")
    # Fetch exactly like routes.py
    cur.execute("SELECT runs, wickets, overs, balls, crr, total_balls FROM match_scores WHERE match_id=%s AND innings=2", (mid,))
    row = cur.fetchone()
    if row:
        print(f"  RESULT TUPLE: {row}")
        print(f"  Mapping as per current routes.py:")
        print(f"    score[0] (runs): {row[0]}")
        print(f"    score[1] (wickets): {row[1]}")
        print(f"    score[2] (overs): {row[2]}")
        print(f"    score[3] (balls): {row[3]}")
        print(f"    score[4] (crr): {row[4]}")
        print(f"    score[5] (total_balls): {row[5]}")
    else:
        print("  No Innings 2 row found.")

conn.close()
