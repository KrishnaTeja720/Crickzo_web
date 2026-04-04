import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="crickai_db"
    )
    cur = conn.cursor(dictionary=True)
    
    print("--- Matches Table (ID 57) ---")
    cur.execute("SELECT * FROM matches WHERE id=57")
    row = cur.fetchone()
    print(row if row else "Match 57 NOT FOUND")
    
    print("\n--- Match Players Table (Match ID 57) ---")
    cur.execute("SELECT * FROM match_players WHERE match_id=57")
    players = cur.fetchall()
    for p in players:
        print(p)
    
    print("\n--- Current Players Table (Match ID 57) ---")
    cur.execute("SELECT * FROM current_players WHERE match_id=57")
    cp = cur.fetchall()
    for c in cp:
        print(c)

    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
