import MySQLdb

try:
    conn = MySQLdb.connect(host="localhost", user="root", password="", db="crickai_db")
    cur = conn.cursor()
    cur.execute("SELECT 1")
    print("MySQL is RUNNING!")
except Exception as e:
    print("MySQL Error:", e)
