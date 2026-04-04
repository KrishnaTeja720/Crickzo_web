import MySQLdb

try:
    conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='', db='crickai_db')
    cur = conn.cursor()
    
    print("Checking users...")
    cur.execute("SELECT id, name, email FROM users")
    users = cur.fetchall()
    for u in users:
        print(f"User ID: {u[0]}, Name: {u[1]}, Email: {u[2]}")
    
    print("\nChecking matches...")
    cur.execute("SELECT id, user_id, team_a, team_b, status FROM matches")
    matches = cur.fetchall()
    for m in matches:
        print(f"Match ID: {m[0]}, Owner (user_id): {m[1]}, Teams: {m[2]} vs {m[3]}, Status: {m[4]}")
        
    conn.close()
except Exception as e:
    print(f"Database debug error: {e}")
