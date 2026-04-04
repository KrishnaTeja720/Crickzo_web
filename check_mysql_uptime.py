import MySQLdb

try:
    conn = MySQLdb.connect(host="localhost", user="root", password="", db="crickai_db")
    cur = conn.cursor()
    cur.execute("SHOW STATUS LIKE 'Uptime'")
    res = cur.fetchone()
    print(f"Uptime: {res[1]} seconds")
    
    # Check connect_timeout
    cur.execute("SHOW VARIABLES LIKE 'connect_timeout'")
    res = cur.fetchone()
    print(f"Connect Timeout: {res[1]}")

except Exception as e:
    print("MySQL Error:", e)
