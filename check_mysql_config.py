import MySQLdb

try:
    conn = MySQLdb.connect(host="localhost", user="root", password="", db="crickai_db")
    cur = conn.cursor()
    
    variables = ["max_connections", "wait_timeout", "interactive_timeout", "max_allowed_packet"]
    for var in variables:
        cur.execute(f"SHOW VARIABLES LIKE '{var}'")
        res = cur.fetchone()
        print(f"{res[0]}: {res[1]}")
    
    cur.execute("SHOW STATUS LIKE 'Max_used_connections'")
    res = cur.fetchone()
    print(f"{res[0]}: {res[1]}")
    
    cur.execute("SHOW STATUS LIKE 'Threads_connected'")
    res = cur.fetchone()
    print(f"{res[0]}: {res[1]}")

    cur.execute("SELECT NOW() - INTERVAL (SELECT VARIABLE_VALUE FROM performance_schema.global_status WHERE VARIABLE_NAME = 'UPTIME') SECOND")
    res = cur.fetchone()
    print(f"Server started at: {res[0]}")

except Exception as e:
    print("MySQL Error:", e)
