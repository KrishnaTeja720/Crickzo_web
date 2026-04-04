import joblib
import numpy as np
import mysql.connector
from sklearn.ensemble import RandomForestClassifier
import os

# Database Configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'crickai_db'
}

def train_model():
    print("[INFO] Connecting to database...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return

    print("[INFO] Extracting match data...")
    # Get all completed matches and their winners
    cur.execute("SELECT id, team_a, team_b, winner FROM matches WHERE status='completed'")
    matches = cur.fetchall()

    if not matches:
        print("[WARNING] No completed matches found in DB. Training with synthetic baseline data...")
        # Create a tiny synthetic dataset to avoid empty training
        # [runs_needed, balls_left, wickets]
        X = np.array([
            [10, 6, 5], [50, 60, 8], [150, 120, 10],  # Winning scenarios for batting
            [30, 6, 2], [100, 30, 3], [5, 1, 1]       # Losing scenarios for batting
        ])
        y = np.array([1, 1, 1, 0, 0, 0])
    else:
        X = []
        y = []
        for m in matches:
            m_id = m['id']
            winner = m['winner']
            
            # Simplified: Batting team is usually the one chasing in 2nd innings
            # We fetch ball-by-ball for 2nd innings
            cur.execute("SELECT runs, wickets_fallen, balls_left FROM ( "
                        "  SELECT SUM(runs+extras) OVER(ORDER BY id) as runs, "
                        "         SUM(CASE WHEN wicket=1 THEN 1 ELSE 0 END) OVER(ORDER BY id) as wickets_fallen, "
                        "         (120 - ROW_NUMBER() OVER(ORDER BY id)) as balls_left " # Assuming T20 for training
                        "  FROM ball_by_ball WHERE match_id=%s AND innings=2"
                        ") as t", (m_id,))
            balls = cur.fetchall()
            
            # Fetch target from 1st innings
            cur.execute("SELECT SUM(runs+extras) FROM ball_by_ball WHERE match_id=%s AND innings=1", (m_id,))
            target_row = cur.fetchone()
            target = (target_row[0] or 150) + 1

            # Get batting team name for 2nd innings 
            # (Rough guess: if Team A bowled 1st, they bat 2nd)
            cur.execute("SELECT team_name FROM match_players WHERE match_id=%s AND innings=2 LIMIT 1", (m_id,))
            batting_team_row = cur.fetchone()
            batting_team = batting_team_row[0] if batting_team_row else m['team_b']

            outcome = 1 if winner == batting_team else 0
            
            for b in balls:
                runs_scored = b['runs']
                wickets_lost = b['wickets_fallen']
                rem_balls = b['balls_left']
                runs_needed = target - runs_scored
                X.append([runs_needed, rem_balls, (10 - wickets_lost)])
                y.append(outcome)

        X = np.array(X)
        y = np.array(y)

    print(f"[INFO] Training on {len(X)} data points...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
    joblib.dump(model, model_path)
    print(f"[SUCCESS] Model trained and saved to {model_path}")

if __name__ == "__main__":
    train_model()
