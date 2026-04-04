import MySQLdb
import config

conn = MySQLdb.connect(host=config.MYSQL_HOST, user=config.MYSQL_USER, passwd=config.MYSQL_PASSWORD, db=config.MYSQL_DB)
cur = conn.cursor()
cur.execute('SELECT team_a, team_b, toss_winner, toss_decision FROM matches WHERE id=71')
print(cur.fetchone())
conn.close()
