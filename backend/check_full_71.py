import MySQLdb
import config

conn = MySQLdb.connect(host=config.MYSQL_HOST, user=config.MYSQL_USER, passwd=config.MYSQL_PASSWORD, db=config.MYSQL_DB)
cur = conn.cursor()
cur.execute('SELECT team_a, team_b, toss_winner, toss_decision FROM matches WHERE id=71')
print("Match Metadata:", cur.fetchone())
cur.execute('SELECT striker, non_striker, bowler FROM current_players WHERE match_id=71')
print("Current Players:", cur.fetchone())
cur.execute('SELECT player_name, team_name FROM match_players WHERE match_id=71')
players = cur.fetchall()
print("Players in Match:")
for p in players:
    print(f"  {p[0]} ({p[1]})")
conn.close()
