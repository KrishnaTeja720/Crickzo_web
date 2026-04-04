import MySQLdb
import config

conn = MySQLdb.connect(host=config.MYSQL_HOST, user=config.MYSQL_USER, passwd=config.MYSQL_PASSWORD, db=config.MYSQL_DB)
cur = conn.cursor()

# Get latest live match
cur.execute("SELECT id, team_a, team_b FROM matches WHERE status='live' ORDER BY id DESC LIMIT 1")
match = cur.fetchone()

if not match:
    print("No live match found.")
else:
    match_id = match[0]
    print(f"DIAGNOSTIC FOR MATCH {match_id}: {match[1]} vs {match[2]}")
    
    # Check both innings
    for inn in [1, 2]:
        print(f"\nINNINGS {inn}:")
        cur.execute("SELECT * FROM match_scores WHERE match_id=%s AND innings=%s", (match_id, inn))
        row = cur.fetchone()
        if row:
            # Print with column names
            cur.execute(f"DESCRIBE match_scores")
            cols = [c[0] for c in cur.fetchall()]
            for name, val in zip(cols, row):
                print(f"  {name}: {val}")
        else:
            print("  No match_scores row found.")

    # Check ball count
    cur.execute("SELECT COUNT(*) FROM ball_by_ball WHERE match_id=%s AND innings=2", (match_id,))
    print(f"\nBALL_BY_BALL count for Innings 2: {cur.fetchone()[0]}")

conn.close()
