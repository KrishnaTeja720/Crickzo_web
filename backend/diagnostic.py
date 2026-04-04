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
    
    # 1. match_scores
    cur.execute("SELECT innings, runs, wickets, overs, balls, total_balls FROM match_scores WHERE match_id=%s", (match_id,))
    print("\nMATCH_SCORES:")
    for row in cur.fetchall():
        print(row)
        
    # 2. current_players
    cur.execute("SELECT striker, non_striker, bowler FROM current_players WHERE match_id=%s", (match_id,))
    print("\nCURRENT_PLAYERS:")
    print(cur.fetchone())
    
    # 3. batsman_stats
    cur.execute("SELECT player_name, runs, balls FROM batsman_stats WHERE match_id=%s", (match_id,))
    print("\nBATSMAN_STATS:")
    for row in cur.fetchall():
        print(row)
        
    # 4. bowler_stats
    cur.execute("SELECT player_name, runs, wickets, overs, balls FROM bowler_stats WHERE match_id=%s", (match_id,))
    print("\nBOWLER_STATS:")
    for row in cur.fetchall():
        print(row)
        
    # 5. ball_by_ball (last 10)
    cur.execute("SELECT innings, over_number, ball_number, batsman, bowler, runs, extras, wicket, extras_type FROM ball_by_ball WHERE match_id=%s ORDER BY id DESC LIMIT 10", (match_id,))
    print("\nBALL_BY_BALL (last 10):")
    for row in cur.fetchall():
        print(row)

conn.close()
