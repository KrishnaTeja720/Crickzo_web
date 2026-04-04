import MySQLdb
try:
    conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='', db='crickai_db')
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM ball_by_ball WHERE match_id=71')
    print(f"Total balls for match 71: {cur.fetchone()[0]}")
    cur.execute('SELECT runs, wickets, balls, total_balls, crr, overs FROM match_scores WHERE match_id=71')
    print(f"Match scores for 71: {cur.fetchall()}")
    cur.execute('SELECT player_name, overs, balls, runs FROM bowler_stats WHERE match_id=71')
    print(f"Bowler stats for 71: {cur.fetchall()}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
