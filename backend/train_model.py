from sklearn.ensemble import HistGradientBoostingClassifier
import os
import joblib
import numpy as np
import pandas as pd
import MySQLdb
from MySQLdb.cursors import DictCursor
import config

# Configuration
DB_CONFIG = {
    'host': config.MYSQL_HOST,
    'user': config.MYSQL_USER,
    'passwd': config.MYSQL_PASSWORD,
    'db': config.MYSQL_DB,
    'cursorclass': DictCursor
}

def get_aggregates():
    """Build historical lookup for teams and players."""
    conn = MySQLdb.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # 1. Team Stats
    cur.execute("SELECT team_a, team_b, winner FROM matches WHERE status='completed'")
    matches = cur.fetchall()
    teams = {}
    for m in matches:
        for t in [m['team_a'], m['team_b']]:
            if t not in teams: teams[t] = {'played': 0, 'won': 0}
            teams[t]['played'] += 1
        if m['winner'] in teams:
            teams[m['winner']]['won'] += 1
    
    team_win_rates = {t: (v['won']/v['played'] if v['played'] > 0 else 0.5) for t, v in teams.items()}
    
    # 2. Player Stats
    cur.execute("SELECT player_name, bat_runs, bat_balls, bowl_balls, bowl_wickets FROM match_players")
    players_data = cur.fetchall()
    players = {}
    for p in players_data:
        name = p['player_name']
        if name not in players: players[name] = {'runs': 0, 'balls_bat': 0, 'balls_bowl': 0, 'wkts': 0}
        players[name]['runs'] += p['bat_runs'] or 0
        players[name]['balls_bat'] += p['bat_balls'] or 0
        players[name]['balls_bowl'] += p['bowl_balls'] or 0
        players[name]['wkts'] += p['bowl_wickets'] or 0
    
    player_stats = {}
    for name, v in players.items():
        sr = (v['runs'] / v['balls_bat'] * 100) if v['balls_bat'] > 0 else 100.0
        wkt_rate = (v['balls_bowl'] / v['wkts']) if v['wkts'] > 0 else 60.0
        player_stats[name] = {'sr': sr, 'wkt_rate': wkt_rate}
        
    conn.close()
    return team_win_rates, player_stats

def fetch_training_data(team_win_rates, player_stats):
    print("[INFO] Fetching and processing training data...")
    conn = MySQLdb.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    cur.execute("SELECT id, team_a, team_b, winner, format FROM matches WHERE status='completed'")
    matches = cur.fetchall()
    
    if len(matches) < 2: return None
    
    X, y = [], []
    
    for m in matches:
        match_id = m['id']
        winner = m['winner']
        total_balls = int(m['format'] or 20) * 6
        
        # Get target
        cur.execute("SELECT SUM(runs + extras_runs) AS total_runs FROM ball_by_ball WHERE match_id=%s AND innings=1", (match_id,))
        row = cur.fetchone()
        target = float(row['total_runs'] or 0) + 1
        
        cur.execute("""
            SELECT DISTINCT b.innings, mp.team_name 
            FROM ball_by_ball b
            JOIN match_players mp ON b.match_id = mp.match_id AND b.batsman = mp.player_name
            WHERE b.match_id = %s
        """, (match_id,))
        team_map = {row['innings']: row['team_name'] for row in cur.fetchall()}
        
        cur.execute("SELECT team_name, player_name FROM match_players WHERE match_id=%s", (match_id,))
        match_roster = cur.fetchall()
        team_aggregates = {}
        for r in match_roster:
            t = r['team_name']
            if t not in team_aggregates: team_aggregates[t] = {'sr': [], 'wkt': []}
            p_stat = player_stats.get(r['player_name'], {'sr': 100.0, 'wkt_rate': 60.0})
            team_aggregates[t]['sr'].append(p_stat['sr'])
            team_aggregates[t]['wkt'].append(p_stat['wkt_rate'])
        
        xi_stats = {t: {'avg_sr': np.mean(v['sr']), 'avg_wkt': np.mean(v['wkt'])} for t, v in team_aggregates.items() if v['sr']}
        
        cur.execute("SELECT innings, runs, extras_runs, wicket FROM ball_by_ball WHERE match_id=%s ORDER BY id", (match_id,))
        balls = cur.fetchall()
        
        c_runs, c_wkts, c_balls = {1:0, 2:0}, {1:0, 2:0}, {1:0, 2:0}
        
        for i, b in enumerate(balls):
            inn = b['innings']
            c_runs[inn] += (b['runs'] or 0) + (b['extras_runs'] or 0)
            c_wkts[inn] += 1 if b['wicket'] else 0
            c_balls[inn] += 1
            
            # Momentum: Last 18 balls (3 overs)
            prev_balls = balls[max(0, i-18):i]
            r_last_18 = sum((px['runs'] or 0) + (px['extras_runs'] or 0) for px in prev_balls)
            w_last_18 = sum(1 for px in prev_balls if px['wicket'])

            # Metrics
            crr = (c_runs[inn] / (c_balls[inn]/6)) if c_balls[inn] > 0 else 0
            balls_left = max(0, total_balls - c_balls[inn])
            rrr = ((target - c_runs[inn]) / (balls_left/6)) if (inn == 2 and balls_left > 0) else 0
            
            bat_team = team_map.get(inn, "Unknown")
            bowl_team = team_map.get(3-inn, "Unknown")
            
            bat_xi = xi_stats.get(bat_team, {'avg_sr': 100.0, 'avg_wkt': 60.0})
            bowl_xi = xi_stats.get(bowl_team, {'avg_sr': 100.0, 'avg_wkt': 60.0})
            
            # Feature Vector (14-D)
            feat = [
                inn, c_runs[inn], c_wkts[inn], c_balls[inn], (target if inn==2 else 0), total_balls,
                crr, rrr, bat_xi['avg_sr'], bowl_xi['avg_wkt'],
                team_win_rates.get(bat_team, 0.5), team_win_rates.get(bowl_team, 0.5),
                r_last_18, w_last_18
            ]
            X.append(feat)
            y.append(1 if winner == bat_team else 0)
            
    conn.close()
    return np.array(X), np.array(y)

def generate_synthetic_data():
    """10,000-sample High-Resolution Simulator for Format-Specific Accuracy."""
    print("[INFO] Generating 10,000 high-resolution synthetic scenarios...")
    X, y = [], []
    # Formats in balls: 2ov(12), 5ov(30), 10ov(60), 20ov(120), 50ov(300)
    formats = [12, 30, 48, 60, 90, 120, 300]
    
    for _ in range(2000): # Iterations to reach ~10k+
        for tb in formats:
            # 1. First Innings Scenarios
            for stage in [0.2, 0.5, 0.8]: # Stage of innings
                b_bowled = int(tb * stage)
                
                # A: Batting Domination
                runs = int(b_bowled * 1.8) # 10.8 RPO
                wkts = int(b_bowled / 24)
                crr = (runs / (b_bowled/6)) if b_bowled > 0 else 10.8
                r18, w18 = int(crr*3), 0 
                X.append([1, runs, wkts, b_bowled, 0, tb, crr, 0, 130.0, 45.0, 0.5, 0.5, r18, w18])
                y.append(1)
                
                # A+: Ultra Batting Domination (Very High CRR)
                ultra_runs = int(b_bowled * 2.8) # 16.8 RPO
                ultra_crr = (ultra_runs / (b_bowled/6)) if b_bowled > 0 else 16.8
                X.append([1, ultra_runs, 0, b_bowled, 0, tb, ultra_crr, 0, 150.0, 40.0, 0.5, 0.5, int(ultra_crr*3), 0])
                y.append(1)

                # B: Bowling Domination
                runs = int(b_bowled * 0.8) # 4.8 RPO
                wkts = int(b_bowled / 6)
                crr = (runs / (b_bowled/6)) if b_bowled > 0 else 4.8
                r18, w18 = int(crr*3), 2
                X.append([1, runs, wkts, b_bowled, 0, tb, crr, 0, 90.0, 75.0, 0.5, 0.5, r18, w18])
                y.append(0)

            # 2. Second Innings (Chasing) Scenarios
            target = float(tb * 1.5) # Average 9 RPO target
            for stage in [0.3, 0.6, 0.9]:
                b_bowled = int(tb * stage)
                b_left = float(tb - b_bowled)
                
                # A: Chasing well (Low RRR)
                runs = int(target * stage * 1.1)
                wkts = int(b_bowled / 20)
                crr = (runs / (b_bowled/6)) if b_bowled > 0 else 9.0
                rrr = ((target - runs) / (b_left/6)) if b_left > 0 else 0
                X.append([2, runs, wkts, b_bowled, target, tb, crr, rrr, 120.0, 50.0, 0.5, 0.5, int(crr*3), 0])
                y.append(1)
                
                # A+: Ultra Chasing Domination (Very High CRR)
                ultra_runs = int(target * stage * 1.5)
                ultra_crr = (ultra_runs / (b_bowled/6)) if b_bowled > 0 else 15.0
                ultra_rrr = ((target - ultra_runs) / (b_left/6)) if b_left > 0 else 0
                X.append([2, ultra_runs, 0, b_bowled, target, tb, ultra_crr, ultra_rrr, 150.0, 40.0, 0.5, 0.5, int(ultra_crr*3), 0])
                y.append(1)

                # B: Collapsing (High RRR)
                runs = int(target * stage * 0.7)
                wkts = int(b_bowled / 8)
                crr = (runs / (b_bowled/6)) if b_bowled > 0 else 5.0
                rrr = ((target - runs) / (b_left/6)) if b_left > 0 else 0
                X.append([2, runs, wkts, b_bowled, target, tb, crr, rrr, 95.0, 75.0, 0.5, 0.5, int(crr*3), 3])
                y.append(0)

    return np.array(X), np.array(y)

def train():
    team_wr, player_stats = {}, {}
    try:
        team_wr, player_stats = get_aggregates()
    except Exception as e:
        print(f"[WARNING] Could not get aggregates: {e}")

    db_data = fetch_training_data(team_wr, player_stats)
    syn_X, syn_y = generate_synthetic_data()
    
    if db_data:
        X = np.vstack([syn_X, db_data[0]])
        y = np.concatenate([syn_y, db_data[1]])
    else:
        X, y = syn_X, syn_y
        
    model = HistGradientBoostingClassifier(max_iter=100, random_state=42)
    model.fit(X, y)
    
    joblib.dump(model, os.path.join(os.path.dirname(__file__), 'model.pkl'))
    print("[SUCCESS] Advanced Gradient Boosting Model trained.")

if __name__ == "__main__":
    train()
