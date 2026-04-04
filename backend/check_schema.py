import MySQLdb
try:
    db = MySQLdb.connect(user="root", passwd="", db="crickai_db")
    cur = db.cursor()
    cur.execute("SELECT DISTINCT status FROM matches")
    rows = cur.fetchall()
    print(f"STATUSES: {rows}")
    db.close()
except Exception as e:
    print(e)
