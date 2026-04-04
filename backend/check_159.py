import mysql.connector
from config import Config

def check_match_159():
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )
    cur = conn.cursor(dictionary=True)
    
    print("--- Match 159 Details ---")
    cur.execute("SELECT * FROM match_scores WHERE match_id=159 AND innings=2")
    print("Score Table:", cur.fetchone())
    
    cur.execute("SELECT * FROM ball_by_ball WHERE match_id=159 AND innings=2 ORDER BY id DESC")
    balls = cur.fetchall()
    print(f"Total balls in BB: {len(balls)}")
    for b in balls:
        print(f"  Ball: {b['bowler']} to {b['batsman']}, runs: {b['runs']}, extras: {b['extras']}")
        
    cur.execute("SELECT * FROM current_players WHERE match_id=159")
    print("Current Players:", cur.fetchone())
    
    conn.close()

if __name__ == "__main__":
    check_match_159()
