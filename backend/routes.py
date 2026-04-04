from flask import Blueprint, request, jsonify
from db import mysql
from flask_bcrypt import Bcrypt
import random
import smtplib
from email.mime.text import MIMEText
import joblib
import numpy as np
import config
import re
import os

routes = Blueprint("routes", __name__)
bcrypt = Bcrypt()

# ======================
# ML MODEL LOADING
# ======================
model = None
def load_match_model():
    """Helper to load the trained ML model from model.pkl."""
    global model
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "model.pkl")
        if os.path.exists(model_path):
            import joblib
            model = joblib.load(model_path)
            print(f"[INFO] ML Model loaded successfully from {model_path}")
        else:
            print(f"[WARNING] model.pkl not found at {model_path}")
    except Exception as e:
        print(f"[ERROR] Model load failed: {e}")

# LOAD ON STARTUP
load_match_model()

# ======================
# IDENTITY HELPERS
# ======================

def get_player_id(player_name):
    """Fetch global player_id by name or create a new one."""
    player_name = (player_name or "").strip()
    if not player_name: return None
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT player_id FROM players WHERE player_name = %s", (player_name,))
    row = cur.fetchone()
    
    if row:
        return row[0]
    
    # Create new global player
    cur.execute("INSERT IGNORE INTO players (player_name) VALUES (%s)", (player_name,))
    mysql.connection.commit()
    
    # Fetch the ID (in case INSERT IGNORE skipped it due to a race condition)
    cur.execute("SELECT player_id FROM players WHERE player_name = %s", (player_name,))
    new_row = cur.fetchone()
    return new_row[0] if new_row else None

def get_or_create_match_player(match_id, player_id, player_name, team_name):
    """Ensure a match_players entry exists for this match and player."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM match_players WHERE match_id = %s AND player_id = %s", (match_id, player_id))
    row = cur.fetchone()
    
    if row:
        return row[0]
    
    # Try to insert (handles case where player was added by name vs by ID)
    # If a row exists with same match_id and player_name but NULL player_id, update it
    cur.execute("SELECT id FROM match_players WHERE match_id = %s AND player_name = %s AND player_id IS NULL", (match_id, player_name))
    null_id_row = cur.fetchone()
    
    if null_id_row:
        cur.execute("UPDATE match_players SET player_id = %s WHERE id = %s", (player_id, null_id_row[0]))
        mysql.connection.commit()
        return null_id_row[0]
        
    # Insert new match roster entry
    cur.execute("""
        INSERT IGNORE INTO match_players (match_id, player_id, player_name, team_name) 
        VALUES (%s, %s, %s, %s)
    """, (match_id, player_id, player_name, team_name))
    mysql.connection.commit()
    
    cur.execute("SELECT id FROM match_players WHERE match_id = %s AND player_id = %s", (match_id, player_id))
    new_row = cur.fetchone()
    return new_row[0] if new_row else None

def get_player_career_stats(player_id):
    """Aggregate career stats for a player from all match_players records."""
    if not player_id: return None
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            SUM(bat_runs) as total_runs, 
            SUM(bat_balls) as total_balls,
            SUM(bowl_wickets) as total_wickets,
            SUM(bowl_runs_conceded) as total_runs_conceded,
            SUM(bowl_balls) as total_bowl_balls,
            COUNT(DISTINCT match_id) as matches_played
        FROM match_players 
        WHERE player_id = %s
    """, (player_id,))
    
    row = cur.fetchone()
    if not row or row[5] == 0:
        return {
            "avg": 25.0, # Baseline
            "sr": 120.0,
            "eco": 8.5,
            "matches": 0
        }
    
    r_runs, b_balls, w_wickets, r_conc, b_bowl, matches = row
    
    # Cast to float for math safety (MySQL SUM/DECIMAL returns Decimal which crashes with float division)
    runs = float(r_runs or 0.0)
    balls = float(b_balls or 0.0)
    wickets = float(w_wickets or 0.0)
    conceded = float(r_conc or 0.0)
    bowled = float(b_bowl or 0.0)
    match_count = float(matches or 0.0)

    if match_count == 0:
        return {"avg": 25.0, "sr": 120.0, "eco": 8.5, "matches": 0}

    return {
        "avg": round(runs / max(1.0, (match_count * 0.8)), 1), 
        "sr": round((runs / max(1.0, balls)) * 100.0, 1),
        "eco": round((conceded / max(1.0, bowled)) * 6.0, 2),
        "matches": int(match_count)
    }


# ======================

@routes.route("/test/echo")
def echo():
    return jsonify({"status": "running", "msg": "API is reloaded"})

@routes.route("/matches/upcoming", methods=["GET"])
def upcoming_matches():
    user_id = request.args.get("user_id")
    if user_id in [None, "null", "undefined", ""]:
        user_id = None
    print(f"[DEBUG] Fetching upcoming matches for user_id: {user_id}")
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT m.id,m.team_a,m.team_b,m.venue,m.format
    FROM matches m
    WHERE m.status='upcoming' AND (%s IS NULL OR m.user_id=%s OR m.user_id IS NULL)
    ORDER BY m.id DESC
    """,(user_id, user_id))
    matches = cur.fetchall()
    return jsonify([{"match_id":m[0],"team_a":m[1],"team_b":m[2],"venue":m[3],"format":m[4], "status": "upcoming"} for m in matches])

# LEGACY ML BLOCK REMOVED

#===================================
#   score engine
#==================================
def update_scoreboard(match_id, innings):

    cur = mysql.connection.cursor()

    # ---------------------
    # AGGREGATE STATS (Python-based for reliability)
    # ---------------------
    cur.execute("""
        SELECT runs, extras, wicket, extras_type 
        FROM ball_by_ball 
        WHERE match_id=%s AND innings=%s
    """, (match_id, innings))
    rows = cur.fetchall()
    
    runs = 0
    wickets = 0
    balls = 0
    
    for r in rows:
        b_runs = r[0] or 0
        b_extras = r[1] or 0
        b_wicket = r[2] or 0
        b_extra_type = (r[3] or "").strip().lower()
        
        runs += (b_runs + b_extras)
        if b_wicket == 1:
            wickets += 1
            
        # Legal ball counting logic
        if b_extra_type not in ["wide", "no_ball", "no ball", "penalty"]:
            balls += 1
            
    # ---------------------
    # OVERS CALCULATION WITH ADJUSTMENTS
    # ---------------------
    cur.execute("SELECT adj_runs, adj_wickets, adj_balls FROM match_scores WHERE match_id=%s AND innings=%s", (match_id, innings))
    ms_row = cur.fetchone()
    adj_runs = ms_row[0] if ms_row and ms_row[0] else 0
    adj_wickets = ms_row[1] if ms_row and ms_row[1] else 0
    adj_balls = ms_row[2] if ms_row and ms_row[2] else 0
    
    runs += adj_runs
    wickets += adj_wickets
    total_balls = balls + adj_balls
    
    overs_count = total_balls // 6
    balls_in_over = total_balls % 6
    overs_display = f"{overs_count}.{balls_in_over}"
    
    if total_balls > 0:
        crr = round((runs * 6) / total_balls, 2)
    else:
        crr = 0.0

    print(f"[DEBUG] update_scoreboard: match={match_id}, inn={innings}, runs={runs}, balls={total_balls}, over={overs_display}, crr={crr}")


    # ---------------------
    # CHECK EXISTING SCORE
    # ---------------------
    cur.execute(
        "SELECT id FROM match_scores WHERE match_id=%s AND innings=%s",
        (match_id,innings)
    )

    exists = cur.fetchone()

    # Get match format for initial total_balls (Max)
    cur.execute("SELECT format FROM matches WHERE id=%s", (match_id,))
    fmt_row = cur.fetchone()
    match_fmt = 20 # Default
    if fmt_row:
        f_num = re.findall(r'\d+', str(fmt_row[0]))
        match_fmt = int(f_num[0]) if f_num else 20
    initial_total_balls = match_fmt * 6

    cur.execute(
        "SELECT id FROM match_scores WHERE match_id=%s AND innings=%s ORDER BY id ASC",
        (match_id,innings)
    )
    all_rows = cur.fetchall()
    
    if all_rows:
        score_id = all_rows[0][0]
        # Keep the first one, delete others
        if len(all_rows) > 1:
            ids_to_delete = [str(r[0]) for r in all_rows[1:]]
            cur.execute(f"DELETE FROM match_scores WHERE id IN ({','.join(ids_to_delete)})")
            print(f"[DEBUG] update_scoreboard: CLEANED UP {len(ids_to_delete)} duplicate rows for match {match_id} inn {innings}")
            
        cur.execute("""
            UPDATE match_scores
            SET runs=%s, wickets=%s, overs=%s, crr=%s, balls=%s
            WHERE id=%s
        """, (runs, wickets, overs_display, crr, total_balls, score_id))
    else:
        cur.execute("""
            INSERT INTO match_scores(match_id, innings, runs, wickets, overs, crr, total_balls, balls)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
        """, (match_id, innings, runs, wickets, overs_display, crr, initial_total_balls, total_balls))



    # ---------------------
    # DYNAMIC STATUS TRANSITION
    # ---------------------
    if total_balls > 0 or runs > 0:
        # Move from 'upcoming' to 'live' if the first ball (or run) is recorded
        cur.execute("UPDATE matches SET status='live' WHERE id=%s AND status='upcoming'", (match_id,))
    elif total_balls == 0 and runs == 0:
        # Move back to 'upcoming' if no scores recorded yet
        cur.execute("""
            UPDATE matches 
            SET status='upcoming' 
            WHERE id=%s AND status='live' AND current_innings=1
        """, (match_id,))

    mysql.connection.commit()

# ======================
# EMAIL FUNCTION
# ======================

def send_email_otp(email, otp):

    sender = "punugotikrishnateja2003@gmail.com"
    password = "ukvstkjicoonuadp"

    msg = MIMEText(f"Your verification code is {otp}")
    msg["Subject"] = "CrickAI OTP"
    msg["From"] = sender
    msg["To"] = email

    server = smtplib.SMTP_SSL("smtp.gmail.com",465)
    server.login(sender,password)
    server.sendmail(sender,email,msg.as_string())
    server.quit()


# ======================
# SIGNUP
# ======================

@routes.route("/signup", methods=["POST"])
def signup():

    data = request.json

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    # -----------------------
    # VALIDATION
    # -----------------------
    if not name or not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    # Strict Validation
    email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    if not re.match(email_regex, email):
        return jsonify({"status":"error", "message": "Invalid email address format"}), 400

    if len(password) < 8:
        return jsonify({"status":"error", "message": "Password must be at least 8 characters"}), 400
    if not any(c.isupper() for c in password):
        return jsonify({"status":"error", "message": "Password must have one uppercase letter"}), 400
    if not any(c.islower() for c in password):
        return jsonify({"status":"error", "message": "Password must have one lowercase letter"}), 400
    if not any(c.isdigit() for c in password):
        return jsonify({"status":"error", "message": "Password must have one number"}), 400
    special_chars = "!@#$%^&*(),.?\":{}|<>"
    if not any(c in special_chars for c in password):
        return jsonify({"status":"error", "message": "Password must have one special character"}), 400

    cur = mysql.connection.cursor()

    # -----------------------
    # CHECK DUPLICATE EMAIL
    # -----------------------
    cur.execute(
        "SELECT id FROM users WHERE email=%s",
        (email,)
    )

    existing_user = cur.fetchone()

    if existing_user:
        return jsonify({
            "status": "error",
            "message": "Email already registered"
        }), 400

    # -----------------------
    # HASH PASSWORD
    # -----------------------
    hashed = bcrypt.generate_password_hash(password).decode("utf-8")



    # =========================
    # CREATE ACCOUNT
    # =========================

    cur.execute(
        "INSERT INTO users(name,email,password) VALUES(%s,%s,%s)",
        (name,email,hashed)
    )

    mysql.connection.commit()

    return jsonify({
        "status":"success",
        "message":"Account created"
    })


# ======================
# LOGIN
# ======================

@routes.route("/login", methods=["POST"])
def login():

    data=request.json
    email=data["email"]
    password=data["password"]

    cur=mysql.connection.cursor()

    cur.execute(
        "SELECT id,password,name FROM users WHERE email=%s",
        (email,)
    )

    user=cur.fetchone()

    if user is not None and bcrypt.check_password_hash(user[1],password):

        return jsonify({
            "status":"success",
            "user_id":user[0],
            "name":user[2]
        })

    return jsonify({"status":"invalid"})


# ======================
# FORGOT PASSWORD
# ======================

@routes.route("/forgot_password", methods=["POST"])
def forgot_password():

    data = request.json
    email = data["email"]

    cur = mysql.connection.cursor()

    # check if email exists
    cur.execute(
        "SELECT id FROM users WHERE email=%s",
        (email,)
    )

    user = cur.fetchone()

    if not user:
        return jsonify({
            "status":"error",
            "message":"Email not registered"
        }),404

    # generate OTP
    otp = str(random.randint(100000,999999))

    # store OTP
    cur.execute(
        "INSERT INTO otp_verification(email,otp) VALUES(%s,%s)",
        (email,otp)
    )

    mysql.connection.commit()

    # send OTP email
    send_email_otp(email,otp)

    return jsonify({
        "status":"success",
        "message":"OTP sent"
    })


# ======================
# RESEND OTP
# ======================

@routes.route("/resend_otp", methods=["POST"])
def resend_otp():

    data=request.json
    email=data["email"]

    otp=str(random.randint(100000,999999))

    cur=mysql.connection.cursor()

    cur.execute(
        "INSERT INTO otp_verification(email,otp) VALUES(%s,%s)",
        (email,otp)
    )

    mysql.connection.commit()

    send_email_otp(email,otp)

    return jsonify({"message":"OTP resent"})


# ======================
# VERIFY OTP
# ======================

@routes.route("/verify_otp", methods=["POST"])
def verify_otp():

    data = request.json

    email = data["email"]
    otp = data["otp"]

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM otp_verification WHERE email=%s AND otp=%s ORDER BY id DESC LIMIT 1",
        (email, otp)
    )

    record = cur.fetchone()

    if record:
        return jsonify({"status": "verified"})
    else:
        return jsonify({"status": "invalid"})


# ======================
# RESET PASSWORD
# ======================

@routes.route("/reset_password", methods=["POST"])
def reset_password():

    data=request.json

    email=data["email"]
    new_password=data["new_password"]

    # Strict Password Validation
    if len(new_password) < 8:
        return jsonify({"status":"error", "message": "Password must be at least 8 characters"}), 400
    if not any(c.isupper() for c in new_password):
        return jsonify({"status":"error", "message": "Password must have one uppercase letter"}), 400
    if not any(c.islower() for c in new_password):
        return jsonify({"status":"error", "message": "Password must have one lowercase letter"}), 400
    if not any(c.isdigit() for c in new_password):
        return jsonify({"status":"error", "message": "Password must have one number"}), 400
    special_chars = "!@#$%^&*(),.?\":{}|<>"
    if not any(c in special_chars for c in new_password):
        return jsonify({"status":"error", "message": "Password must have one special character"}), 400

    hashed=bcrypt.generate_password_hash(new_password).decode("utf-8")

    cur=mysql.connection.cursor()

    cur.execute(
        "UPDATE users SET password=%s WHERE email=%s",
        (hashed,email)
    )

    mysql.connection.commit()

    return jsonify({"message":"Password updated"})

# ======================
# UPDATE PROFILE
# ======================
@routes.route("/user/update_profile", methods=["POST"])
def update_profile():
    data = request.json
    user_id = data.get("user_id")
    name = data.get("name")
    email = data.get("email")

    if not all([user_id, name, email]):
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    cur = mysql.connection.cursor()
    try:
        cur.execute("UPDATE users SET name=%s, email=%s WHERE id=%s", (name, email, user_id))
        mysql.connection.commit()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "success", "message": "Profile updated"})

# ======================
# CHANGE PASSWORD
# ======================
@routes.route("/user/change_password", methods=["POST"])
def change_password():
    data = request.json
    user_id = data.get("user_id")
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not all([user_id, old_password, new_password]):
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    # Password validation (same as signup)
    if len(new_password) < 8:
        return jsonify({"status":"error", "message": "New password must be at least 8 characters"}), 400
    if not any(c.isupper() for c in new_password):
        return jsonify({"status":"error", "message": "New password must have one uppercase letter"}), 400
    if not any(c.islower() for c in new_password):
        return jsonify({"status":"error", "message": "New password must have one lowercase letter"}), 400
    if not any(c.isdigit() for c in new_password):
        return jsonify({"status":"error", "message": "New password must have one number"}), 400
    special_chars = "!@#$%^&*(),.?\":{}|<>"
    if not any(c in special_chars for c in new_password):
        return jsonify({"status":"error", "message": "New password must have one special character"}), 400

    cur = mysql.connection.cursor()
    cur.execute("SELECT password FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()

    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    hashed_old = user[0]
    if not bcrypt.check_password_hash(hashed_old, old_password):
        return jsonify({"status": "error", "message": "Incorrect old password"}), 400

    hashed_new = bcrypt.generate_password_hash(new_password).decode("utf-8")
    cur.execute("UPDATE users SET password=%s WHERE id=%s", (hashed_new, user_id))
    mysql.connection.commit()

    return jsonify({"status": "success", "message": "Password updated"})

#==========================================
# MATCH DETAILS
#==========================================
@routes.route("/match/details/<match_id>", methods=["GET"])
def match_details(match_id):

    cur = mysql.connection.cursor()

    # match info
    cur.execute("""
    SELECT team_a,team_b,venue,format,toss_winner,toss_decision,status
    FROM matches
    WHERE id=%s
    """,(match_id,))

    match = cur.fetchone()

    # safety if match not found
    if not match:
        return jsonify({"error":"Match not found"}),404

    # Authoritative fetch for all innings scores
    cur.execute("SELECT runs,wickets,overs,crr,innings FROM match_scores WHERE match_id=%s",(match_id,))
    scores = cur.fetchall()
    score_map = {s[4]: {"runs": s[0], "wickets": s[1], "overs": s[2], "crr": s[3]} for s in scores}

    # Determine active scoreboard for the top-level response
    cur.execute("SELECT current_innings FROM matches WHERE id=%s", (match_id,))
    m_row = cur.fetchone()
    active_inn = m_row[0] if m_row else 1
    
    # GROUND TRUTH OVERRIDE: Proactively rebuild if 0/0 but balls exist
    for inn in [1, 2]:
        cur.execute("SELECT SUM(runs + (extras - IF(extras_type IN ('bye','legbye','penalty'), extras, 0))), SUM(wicket), COUNT(*) FROM ball_by_ball WHERE match_id=%s AND innings=%s", (match_id, inn))
        bb = cur.fetchone()
        bb_runs = int(bb[0] or 0) if bb else 0
        bb_balls = int(bb[2] or 0) if bb else 0
        
        if bb_balls > 0 and (score_map.get(inn, {}).get("runs", 0) == 0):
            print(f"[REBUILD] match/details auto-syncing match {match_id} inn {inn}")
            update_scoreboard(match_id, inn)
            # Re-fetch
            cur.execute("SELECT runs, wickets, overs, crr FROM match_scores WHERE match_id=%s AND innings=%s", (match_id, inn))
            res_upd = cur.fetchone()
            if res_upd:
                score_map[inn] = {"runs": res_upd[0], "wickets": res_upd[1], "overs": res_upd[2], "crr": res_upd[3]}

    # Top-level score should reflect the LIVE innings for correct App display
    main_score = score_map.get(active_inn, {"runs": 0, "wickets": 0, "overs": "0.0", "crr": 0.0})

    return jsonify({
        "team_a": match[0], "team_b": match[1], "venue": match[2], "format": match[3],
        "toss_winner": match[4], "toss_decision": match[5], "status": match[6],
        "runs": main_score["runs"], "wickets": main_score["wickets"],
        "overs": main_score["overs"], "crr": main_score["crr"],
        "current_innings": active_inn,
        "teamAScore": score_map.get(1), "teamBScore": score_map.get(2)
    })


# ======================
# CREATE MATCH
# ======================

@routes.route("/match/create", methods=["POST"])
def create_match():

    data = request.json

    user_id = data.get("user_id")

    if user_id is None or user_id <= 0:
        return jsonify({"error":"user_id missing"}),400

    cur = mysql.connection.cursor()

    cur.execute("""
    INSERT INTO matches(user_id,team_a,team_b,format,venue,toss_winner,toss_decision,pitch_type,weather,status,current_innings)
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,'upcoming',0)
    """,
    (
        user_id,
        data["team_a"],
        data["team_b"],
        int(data.get("format", 20) or 20),
        data.get("venue",""),
        data["toss"],
        data.get("toss_decision","Batting"),
        data["pitch"],
        data["weather"]
    ))
    mysql.connection.commit()

    # GET AUTO GENERATED MATCH ID
    match_id = cur.lastrowid

    # RETURN MATCH ID TO ANDROID
    return jsonify({
        "status": "success",
        "match_id": match_id,
        "message": "Match created successfully"
    })

# ======================
# LIVE MATCHES
# ======================
@routes.route("/matches/live", methods=["GET"])
def live_matches():
    user_id = request.args.get("user_id")
    if user_id in [None, "null", "undefined", ""]:
        user_id = None
    with open("debug_matches.log", "a") as f:
        f.write(f"FETCH LIVE MATCHES - user_id: {user_id}\n")
    print(f"[DEBUG] Fetching live matches for user_id: {user_id}")

    cur = mysql.connection.cursor()

    cur.execute("""
    SELECT m.id,m.team_a,m.team_b,m.venue,
           COALESCE(s1.runs, 0), COALESCE(s1.wickets, 0),
           COALESCE(s2.runs, 0), COALESCE(s2.wickets, 0), COALESCE(s2.overs, '0.0'), COALESCE(s2.crr, 0.0), 
           m.current_innings, m.format, m.toss_winner, m.toss_decision, m.status
    FROM matches m
    LEFT JOIN match_scores s1 ON m.id = s1.match_id AND s1.innings = 1
    LEFT JOIN match_scores s2 ON m.id = s2.match_id AND m.current_innings = s2.innings
    WHERE m.status = 'live' AND (%s IS NULL OR m.user_id=%s OR m.user_id IS NULL)
    ORDER BY m.id DESC
    """, (user_id, user_id))

    rows = cur.fetchall()
    result = []
    
    for r in rows:
        match_id = r[0]
        curr_inn = r[10]
        
        # GROUND TRUTH OVERRIDE: Check if ball_by_ball has more info than the summary table
        cur.execute("SELECT SUM(runs + extras), SUM(wicket), COUNT(*) FROM ball_by_ball WHERE match_id=%s AND innings=%s", (match_id, curr_inn))
        bb = cur.fetchone()
        bb_runs = int(bb[0] or 0) if bb else 0
        bb_wickets = int(bb[1] or 0) if bb else 0
        
        m_runs = r[6] if curr_inn == 2 else r[4]
        m_wickets = r[7] if curr_inn == 2 else r[5]
        
        final_runs = max(bb_runs, m_runs)
        final_wickets = max(bb_wickets, m_wickets)

        result.append({
            "match_id": match_id,
            "team_a": r[1],
            "team_b": r[2],
            "venue": r[3],
            "inn1_runs": r[4],
            "inn1_wickets": r[5],
            "runs": final_runs,
            "wickets": final_wickets,
            "overs": r[8],
            "crr": r[9],
            "current_innings": curr_inn,
            "format": r[11],
            "toss_winner": r[12],
            "toss_decision": r[13],
            "status": r[14]
        })

    return jsonify(result)

# ======================
# RECOMPUTE SCORE
# ======================
@routes.route("/match/recompute_score", methods=["POST"])
def recompute_score():
    """Force recalculate match scores from ball_by_ball table and update match_scores."""
    data = request.json
    match_id = data.get("match_id")
    innings = data.get("innings", 1)

    if not match_id:
        return jsonify({"status": "error", "message": "match_id is required"}), 400

    try:
        # Recompute for the requested innings
        update_scoreboard(match_id, innings)
        # Also recompute innings 1 if we are in innings 2, to keep data consistent
        if innings == 2:
            update_scoreboard(match_id, 1)
        return jsonify({"status": "success", "message": f"Score recomputed for match {match_id}, innings {innings}"})
    except Exception as e:
        print(f"[ERROR] recompute_score failed for match {match_id}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ======================
# FETCH PLAYERS
# ======================

@routes.route("/match/players/<int:match_id>", methods=["GET"])
def get_match_players(match_id):
    """Fetch all players in a match with their global IDs."""
    print(f"[DEBUG] Fetching players for MATCH {match_id}")
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT player_id, player_name, team_name, role 
        FROM match_players 
        WHERE match_id = %s
    """, (match_id,))
    rows = cur.fetchall()
    
    result = []
    for r in rows:
        result.append({
            "player_id": r[0],
            "player_name": r[1],
            "team_name": r[2],
            "role": r[3]
        })
    return jsonify(result)

# ======================
# TEAM PLAYERS ROSTER
# ======================

@routes.route("/team/players/<team_name>", methods=["GET"])
def get_team_players_roster(team_name):
    print(f"[DEBUG] Fetching GLOBAL players for TEAM {team_name}")
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT player_id, player_name
            FROM players
            WHERE team_name=%s
        """, (team_name,))
        players = cur.fetchall()
        
        # If empty, return a helpful message or empty list
        return jsonify([
            {"id": p[0], "name": p[1]} for p in players
        ])
    except Exception as e:
        print(f"ERROR: Could not fetch players for {team_name}: {e}")
        return jsonify({"error": "Database connection failed", "details": str(e)}), 500


# ======================
# START MATCH
# ======================

@routes.route("/match/start", methods=["POST"])
def start_match():

    data = request.json

    match_id = data.get("match_id")
    striker = (data.get("striker") or "").strip()
    non_striker = (data.get("non_striker") or "").strip()
    bowler = (data.get("bowler") or "").strip()

    if not match_id or not striker or not non_striker or not bowler:
        return jsonify({"error":"Missing fields"}),400

    print(f"DEBUG: start_match call for mid={match_id}, striker={striker}, non_striker={non_striker}, bowler={bowler}")
    
    cur = mysql.connection.cursor()

    # -----------------------
    # CHECK MATCH EXISTS
    # -----------------------
    cur.execute("SELECT id FROM matches WHERE id=%s",(match_id,))
    match = cur.fetchone()
    print(f"DEBUG: Match check result: {match}")

    if not match:
        print(f"DEBUG: Match {match_id} NOT FOUND in start_match")
        return jsonify({"error":"Match not found"}),404


    # -----------------------
    # CLEAR PREVIOUS DATA
    # -----------------------
    print(f"DEBUG: Clearing previous data for match {match_id}")
    cur.execute("DELETE FROM current_players WHERE match_id=%s",(match_id,))
    cur.execute("DELETE FROM batsman_stats WHERE match_id=%s",(match_id,))
    cur.execute("DELETE FROM bowler_stats WHERE match_id=%s",(match_id,))
    cur.execute("DELETE FROM match_scores WHERE match_id=%s",(match_id,))


    # -----------------------
    # INSERT CURRENT PLAYERS
    # -----------------------
    cur.execute("""
    INSERT INTO current_players(match_id,striker,non_striker,bowler)
    VALUES(%s,%s,%s,%s)
    """,(match_id,striker,non_striker,bowler))


    # -----------------------
    # INITIALIZE BATSMAN STATS
    # -----------------------
    cur.execute("""
    INSERT INTO batsman_stats(match_id,player_name,runs,balls,fours,sixes)
    VALUES(%s,%s,0,0,0,0)
    """,(match_id,striker))

    cur.execute("""
    INSERT INTO batsman_stats(match_id,player_name,runs,balls,fours,sixes)
    VALUES(%s,%s,0,0,0,0)
    """,(match_id,non_striker))


    # -----------------------
    # INITIALIZE BOWLER STATS
    # -----------------------
    cur.execute("""
    INSERT INTO bowler_stats(match_id,player_name,overs,maidens,runs,wickets,balls)
    VALUES(%s,%s,0,0,0,0,0)
    """,(match_id,bowler))


    # -----------------------
    # INITIALIZE SCOREBOARD
    # -----------------------
    print(f"DEBUG: Initializing scoreboard for match {match_id}")
    cur.execute("UPDATE matches SET current_innings=1 WHERE id=%s",(match_id,))
    
    cur.execute("""
INSERT INTO match_scores(match_id,innings,runs,wickets,overs,crr,total_balls)
VALUES(%s,%s,0,0,0,0,0)
""",(match_id,1))


    mysql.connection.commit()
    print(f"DEBUG: Match {match_id} successfully started and committed")

    return jsonify({
        "status":"success",
        "message":"Match started",
        "striker":striker,
        "non_striker":non_striker,
        "bowler":bowler
    })

# =========================
# UNIFIED STATS ENGINE
# =========================

def update_batsman_stats(match_id, batsman, runs, counts_as_ball=True):
    batsman = (batsman or "").strip()
    if not batsman: return
    
    player_id = get_player_id(batsman)
    if not player_id: return
    
    cur = mysql.connection.cursor()
    # Ensure entry exists
    mid_pid = get_or_create_match_player(match_id, player_id, batsman, "Unknown")
    
    cur.execute("""
        SELECT bat_runs, bat_balls, bat_fours, bat_sixes
        FROM match_players
        WHERE id=%s
    """, (mid_pid,))
    data = cur.fetchone()

    ball_count = 1 if counts_as_ball else 0

    if data:
        runs_old, balls_old, fours_old, sixes_old = data
        runs_old += runs
        balls_old += ball_count
        if runs == 4: fours_old += 1
        if runs == 6: sixes_old += 1

        cur.execute("""
            UPDATE match_players
            SET bat_runs=%s, bat_balls=%s, bat_fours=%s, bat_sixes=%s
            WHERE id=%s
        """, (runs_old, balls_old, fours_old, sixes_old, mid_pid))
        
        # Legacy Sync (Optional, but keeping for compatibility during transition)
        cur.execute("UPDATE batsman_stats SET runs=%s, balls=%s, fours=%s, sixes=%s WHERE match_id=%s AND player_name=%s", (runs_old, balls_old, fours_old, sixes_old, match_id, batsman))
        
    mysql.connection.commit()

def update_bowler_stats(match_id, bowler, runs_to_add, counts_as_ball, wicket):
    bowler = (bowler or "").strip()
    if not bowler: return
    
    player_id = get_player_id(bowler)
    if not player_id: return
    
    cur = mysql.connection.cursor()
    mid_pid = get_or_create_match_player(match_id, player_id, bowler, "Unknown")
    
    cur.execute("""
        SELECT bowl_runs_conceded, bowl_wickets, bowl_balls, bowl_maidens
        FROM match_players
        WHERE id=%s
    """, (mid_pid,))
    data = cur.fetchone()

    if data:
        r_old, w_old, b_old, m_old = data
        new_runs = r_old + runs_to_add
        new_wickets = w_old + wicket
        new_balls = b_old + (1 if counts_as_ball else 0)
        
        ov = new_balls // 6
        bl = new_balls % 6
        overs_display = f"{ov}.{bl}"

        cur.execute("""
            UPDATE match_players
            SET bowl_runs_conceded=%s, bowl_wickets=%s, bowl_overs=%s, bowl_balls=%s, bowl_maidens=%s
            WHERE id=%s
        """, (new_runs, new_wickets, overs_display, new_balls, m_old, mid_pid))
        
        # Legacy Sync
        cur.execute("UPDATE bowler_stats SET runs=%s, wickets=%s, overs=%s, balls=%s, maidens=%s WHERE match_id=%s AND player_name=%s", (new_runs, new_wickets, overs_display, new_balls, m_old, match_id, bowler))
        
    mysql.connection.commit()


# =========================
# PARTNERSHIP ENGINE
# =========================
def calculate_partnership(match_id, innings):

    cur = mysql.connection.cursor()

    # --------------------------
    # GET CURRENT BATSMEN
    # --------------------------
    cur.execute("""
        SELECT striker, non_striker
        FROM current_players
        WHERE match_id=%s
    """,(match_id,))

    players = cur.fetchone()

    # if match not started yet
    if not players:
        return {
            "striker": "",
            "non_striker": "",
            "runs": 0,
            "balls": 0
        }

    striker = players[0]
    non_striker = players[1]

    # --------------------------
    # FIND LAST WICKET
    # --------------------------
    cur.execute("""
        SELECT id
        FROM ball_by_ball
        WHERE match_id=%s AND wicket=1
        ORDER BY id DESC
        LIMIT 1
    """,(match_id,))

    last_wicket = cur.fetchone()

    # --------------------------
    # CALCULATE PARTNERSHIP
    # --------------------------
    if last_wicket:

        last_id = last_wicket[0]

        cur.execute("""
            SELECT SUM(runs + extras), COUNT(*)
            FROM ball_by_ball
            WHERE match_id=%s AND innings=%s AND id>%s
        """,(match_id,innings,last_id))

    else:

        cur.execute("""
            SELECT SUM(runs + extras), COUNT(*)
FROM ball_by_ball
WHERE match_id=%s AND innings=%s
        """,(match_id,innings,))

    data = cur.fetchone()

    runs = int(data[0]) if data and data[0] is not None else 0
    balls = int(data[1]) if data and data[1] is not None else 0

    return {
        "striker": striker,
        "non_striker": non_striker,
        "runs": runs,
        "balls": balls
    }

#==============================================
# FETCH BATSMEN STATS (API)
#==============================================
@routes.route("/match/batsmen/<match_id>", methods=["GET"])
def batsmen_api(match_id):
    innings = request.args.get("innings", 1)
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT batsman, SUM(runs), COUNT(*), SUM(CASE WHEN runs=4 THEN 1 ELSE 0 END), SUM(CASE WHEN runs=6 THEN 1 ELSE 0 END)
        FROM ball_by_ball
        WHERE match_id=%s AND innings=%s AND (extras_type IS NULL OR extras_type != 'wide')
        GROUP BY batsman
    """, (match_id, innings))

    players = cur.fetchall()
    result = []

    for p in players:
        name, runs, balls, fours, sixes = p
        runs = int(runs or 0)
        balls = int(balls or 0)
        fours = int(fours or 0)
        sixes = int(sixes or 0)
        sr = round((runs / balls) * 100, 2) if balls > 0 else 0

        result.append({
            "batsman": name,
            "runs": runs,
            "balls": balls,
            "fours": fours,
            "sixes": sixes,
            "strike_rate": sr 
        })
    return jsonify(result)

#=================================================
#   FETCH BOWLER STATS (API)
#=================================================
@routes.route("/match/bowler/<match_id>", methods=["GET"])
def bowler_stat_api(match_id):
    innings = request.args.get("innings", 1)
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT bowler, SUM(runs + extras), SUM(wicket), COUNT(*), 
               SUM(CASE WHEN runs=0 AND extras=0 THEN 1 ELSE 0 END)
        FROM ball_by_ball
        WHERE match_id=%s AND innings=%s 
        AND (extras_type IS NULL OR LOWER(TRIM(extras_type)) NOT IN ('wide', 'no_ball', 'no ball', 'penalty'))
        GROUP BY bowler
    """, (match_id, innings))

    bowlers = cur.fetchall()
    result = []

    for b in bowlers:
        p_name, runs, wickets, balls, dot_balls = b
        runs = int(runs or 0)
        wickets = int(wickets or 0)
        balls = int(balls or 0)
        
        overs_str = f"{balls // 6}.{balls % 6}"
        
        if balls > 0:
            economy = round(runs / (balls / 6.0), 2)
        else:
            economy = 0

        result.append({
            "bowler": p_name,
            "overs": overs_str,
            "runs": runs,
            "wickets": wickets,
            "maidens": 0,
            "economy": economy
        })
    return jsonify(result)

#======================================================
# PARTNERSHIP (API)
#=======================================================
@routes.route("/match/partnership/<match_id>")
def partnership_api(match_id):

    innings = request.args.get("innings")

    data = calculate_partnership(match_id, innings)

    return jsonify({
        "striker": data["striker"],
        "non_striker": data["non_striker"],
        "runs": data["runs"],
        "balls": data["balls"]
    })

#=====================================================
# MATCH SETUP (API)
#================================================++++
@routes.route("/match/setup", methods=["POST", "OPTIONS"])
def match_setup():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.json
    print(f"DEBUG: /match/setup called with data: {data}")
    match_id = data.get("match_id")
    team_a_players = data.get("team_a_players", [])
    team_b_players = data.get("team_b_players", [])

    if not match_id:
        print("DEBUG: /match/setup failed - no match_id")
        return jsonify({"error": "Missing match_id"}), 400

    cur = mysql.connection.cursor()
    
    # Fetch actual team names
    cur.execute("SELECT team_a, team_b FROM matches WHERE id=%s", (match_id,))
    match = cur.fetchone()
    if not match:
        return jsonify({"error": "Match not found"}), 404
    
    team_a_name, team_b_name = match

    # Clear existing players to avoid duplicates
    cur.execute("DELETE FROM match_players WHERE match_id=%s", (match_id,))

    for player_name in team_a_players:
        pid = get_player_id(player_name)
        cur.execute("""
            INSERT INTO match_players(match_id, player_id, player_name, team_name)
            VALUES(%s,%s,%s,%s)
        """, (match_id, pid, player_name, team_a_name))

    for player_name in team_b_players:
        pid = get_player_id(player_name)
        cur.execute("""
            INSERT INTO match_players(match_id, player_id, player_name, team_name)
            VALUES(%s,%s,%s,%s)
        """, (match_id, pid, player_name, team_b_name))

    mysql.connection.commit()

    return jsonify({"message":"Players synced successfully"})

@routes.route("/match/add_player", methods=["POST", "OPTIONS"])
def add_player():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    data = request.json
    print(f"DEBUG: /match/add_player CALLED with data: {data}")
    
    match_id = data.get("match_id")
    player_name = data.get("player_name")
    team_identifier = data.get("team") or data.get("team_name")

    if not match_id:
        return jsonify({"error": "Missing match_id"}), 400
    if not player_name:
        return jsonify({"error": "Missing player_name"}), 400
    if not team_identifier:
        return jsonify({"error": "Missing team identifier (A/B)"}), 400

    cur = mysql.connection.cursor()
    
    # Resolve team name
    team_name = team_identifier
    norm_id = str(team_identifier).strip().upper()
    if norm_id in ["A", "B", "TEAMA", "TEAMB", "TEAM A", "TEAM B"]:
        cur.execute("SELECT team_a, team_b FROM matches WHERE id=%s", (match_id,))
        match_info = cur.fetchone()
        if match_info:
            team_name = match_info[0] if "A" in norm_id else match_info[1]

    # Global Identity
    pid = get_player_id(player_name)
    
    print(f"DEBUG: Inserting into match_players: match_id={match_id}, pid={pid}, player='{player_name}', team='{team_name}'")
    try:
        cur.execute("""
            INSERT INTO match_players(match_id, player_id, player_name, team_name, role)
            VALUES(%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE player_id=VALUES(player_id)
        """, (match_id, pid, player_name, team_name, None))
        mysql.connection.commit()
    except Exception as e:
        print(f"DEBUG: Error inserting player: {str(e)}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "success", "message": f"Player added to {team_name}"})

@routes.route("/match/remove_player", methods=["POST", "OPTIONS"])
def remove_player():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    data = request.json
    match_id = data.get("match_id")
    player_name = data.get("player_name")
    team_name = data.get("team_name") or data.get("team")

    if not all([match_id, player_name, team_name]):
        return jsonify({"error": "Missing fields"}), 400

    cur = mysql.connection.cursor()
    cur.execute("""
        DELETE FROM match_players 
        WHERE match_id=%s AND player_name=%s AND team_name=%s
    """, (match_id, player_name, team_name))
    mysql.connection.commit()

    return jsonify({"status": "success", "message": "Player removed"})

#=================================================
#  MATCH BALL (API)
#=================================================
@routes.route("/match/ball", methods=["POST"])
def ball_input():
    try:
        data = request.get_json(silent=True)
        print("BALL DATA:", data)
        if not data:
            return jsonify({
                "status": "error",
                "message": "Invalid or empty JSON"
            }), 400

        match_id = data.get("match_id")
        innings = data.get("innings", 1)
        
        # 1. Fetch current players if not provided
        cur = mysql.connection.cursor()
        cur.execute("SELECT striker, non_striker, bowler FROM current_players WHERE match_id=%s", (match_id,))
        players = cur.fetchone()
        if not players:
            return jsonify({"error": "Match not started"}), 400
        
        striker, non_striker, bowler = players
        striker = striker.strip() if striker else ""
        non_striker = non_striker.strip() if non_striker else ""
        bowler = bowler.strip() if bowler else ""
        
        # 2. Get ball details from payload
        batsman_runs = int(data.get("runs", 0))
        extra_type = data.get("extra_type")
        if extra_type:
            extra_type = extra_type.strip().lower()
        is_wicket = data.get("is_wicket", False)
        new_batsman = (data.get("new_batsman") or "").strip()
        
        # 3. Logic for runs and extras
        extras_for_scoreboard = 0
        batsman_runs_for_stats = batsman_runs
        counts_as_ball_batsman = True
        counts_as_ball_bowler = True
        bowler_runs_for_stats = 0

        if extra_type == "wide":
            extras_for_scoreboard = 1 + batsman_runs
            batsman_runs_for_stats = 0
            counts_as_ball_batsman = False
            counts_as_ball_bowler = False
            bowler_runs_for_stats = extras_for_scoreboard # Wide runs are credited to bowler
        elif extra_type == "no_ball":
            extras_for_scoreboard = 1
            # batsman_runs_for_stats remains incoming runs
            counts_as_ball_batsman = True # No balls count as balls for batsman
            counts_as_ball_bowler = False
            bowler_runs_for_stats = 1 + batsman_runs_for_stats # 1 extra + whatever batsman scored
        elif extra_type in ["bye", "legbye"]:
            extras_for_scoreboard = batsman_runs
            batsman_runs_for_stats = 0
            counts_as_ball_batsman = True
            counts_as_ball_bowler = True
            bowler_runs_for_stats = 0 # Bowler not responsible for byes/legbyes
        elif extra_type == "penalty":
            extras_for_scoreboard = batsman_runs
            batsman_runs_for_stats = 0
            counts_as_ball_batsman = False
            counts_as_ball_bowler = False
            bowler_runs_for_stats = 0
        else: # Normal ball
            extras_for_scoreboard = 0
            counts_as_ball_batsman = True
            counts_as_ball_bowler = True
            bowler_runs_for_stats = batsman_runs_for_stats

        total_ball_runs = batsman_runs_for_stats + extras_for_scoreboard
        wicket_val = 1 if is_wicket else 0
        legal_ball = counts_as_ball_bowler

        # 4. Ball Calculation
        cur.execute("SELECT total_balls FROM match_scores WHERE match_id=%s AND innings=%s", (match_id, innings))
        tb_row = cur.fetchone()
        current_total_balls = int(tb_row[0] or 0) if tb_row else 0
        
        if legal_ball:
            current_total_balls += 1
            
        over_num = current_total_balls // 6
        ball_in_over = current_total_balls % 6
        overs_display = f"{over_num}.{ball_in_over}"

        # 5. Insert Ball
        cur.execute("""
            INSERT INTO ball_by_ball(match_id, innings, over_number, ball_number, batsman, bowler, runs, extras, extras_type, extras_runs, wicket, striker, non_striker)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (match_id, innings, over_num, ball_in_over, striker, bowler, batsman_runs_for_stats, extras_for_scoreboard, extra_type, extras_for_scoreboard, wicket_val, striker, non_striker))

        # 6. Update Stats
        # (Removed redundant manual match_scores update - update_scoreboard handles it)

        # IMPORTANT: Run these helper functions WITHOUT individual commits
        update_scoreboard(match_id, innings)
        update_batsman_stats(match_id, striker, batsman_runs_for_stats, counts_as_ball_batsman)
        update_bowler_stats(match_id, bowler, bowler_runs_for_stats, counts_as_ball_bowler, wicket_val)

        # 7. Strike Rotation & Wicket & Bowler Reset
        cur.execute("SELECT striker, non_striker FROM current_players WHERE match_id=%s", (match_id,))
        p_row = cur.fetchone()
        s_prev, ns_prev = p_row if p_row else ("Unknown", "Unknown")
        
        out_batsman = data.get("out_batsman", striker)

        s_new, ns_new = s_prev, ns_prev

        # Wicket update
        if is_wicket and new_batsman:
            if out_batsman == ns_prev:
                ns_new = new_batsman
            else:
                s_new = new_batsman
                
            # Ensure stats exist
            cur.execute("SELECT id FROM batsman_stats WHERE match_id=%s AND player_name=%s", (match_id, new_batsman))
            if not cur.fetchone():
                cur.execute("INSERT INTO batsman_stats(match_id, player_name, runs, balls, fours, sixes) VALUES(%s,%s,0,0,0,0)", (match_id, new_batsman))
            print(f"[DEBUG] Wicket: {out_batsman} replaced by {new_batsman}")
        
        # Odd runs rotation (only if not a wicket, usually)
        if not is_wicket and (batsman_runs % 2 != 0):
            s_new, ns_new = ns_new, s_new
            print(f"[DEBUG] Odd Runs ({batsman_runs}): Rotate {s_prev}/{ns_prev} -> {s_new}/{ns_new}")

        # Over end rotation
        if legal_ball and ball_in_over == 0 and current_total_balls > 0:
            s_new, ns_new = ns_new, s_new
            cur.execute("UPDATE current_players SET bowler=NULL WHERE match_id=%s", (match_id,))
            print(f"[DEBUG] End of Over: Rotate {s_new}/{ns_new}")

        # Final DB Update
        if s_new != s_prev or ns_new != ns_prev:
            cur.execute("UPDATE current_players SET striker=%s, non_striker=%s WHERE match_id=%s", (s_new, ns_new, match_id))
            print(f"[DEBUG] Final Strike Sync: Striker={s_new}, Non-striker={ns_new}")

        # SINGLE COMMIT for the entire transaction
        mysql.connection.commit()
        
        return jsonify({
            "status": "success", 
            "message": "Ball saved",
            "over": over_num,
            "ball": ball_in_over
        })

    except Exception as e:
        print("BALL ERROR:", e)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ======================
# REBUILD MATCH STATE
# ======================

def rebuild_match_state(match_id):
    cur = mysql.connection.cursor()
    
    # 1. Reset everything (Clearing manual adjustments too)
    cur.execute("UPDATE match_players SET bat_runs=0, bat_balls=0, bat_fours=0, bat_sixes=0, bowl_runs_conceded=0, bowl_wickets=0, bowl_overs='0.0', bowl_balls=0, bowl_maidens=0 WHERE match_id=%s", (match_id,))
    cur.execute("UPDATE batsman_stats SET runs=0, balls=0, fours=0, sixes=0 WHERE match_id=%s", (match_id,))
    cur.execute("UPDATE bowler_stats SET overs='0.0', balls=0, maidens=0, runs=0, wickets=0 WHERE match_id=%s", (match_id,))
    cur.execute("UPDATE match_scores SET runs=0, wickets=0, overs='0.0', crr=0, total_balls=0, adj_runs=0, adj_wickets=0, adj_balls=0 WHERE match_id=%s", (match_id,))
    
    # 2. Re-simulate all balls
    cur.execute("SELECT innings, batsman, bowler, runs, extras, wicket, extras_type FROM ball_by_ball WHERE match_id=%s ORDER BY id ASC", (match_id,))
    balls = cur.fetchall()
    
    # Track balls per innings to fix total_balls
    total_balls_by_innings = {1: 0, 2: 0}
    
    for ball in balls:
        innings_ball, batsman, bowler, runs, extras, wicket, extra_type = ball
        batsman = (batsman or "").strip()
        bowler = (bowler or "").strip()
        
        counts_as_ball_batsman = True
        counts_as_ball_bowler = True
        bowler_runs_for_stats = 0
        batsman_runs_for_stats = runs

        e_type_norm = (extra_type or "").strip().lower()
        if e_type_norm == "wide":
            batsman_runs_for_stats = 0
            counts_as_ball_batsman = False
            counts_as_ball_bowler = False
            bowler_runs_for_stats = extras # extras column stores 1+R for wide
        elif e_type_norm == "no_ball":
            counts_as_ball_batsman = True
            counts_as_ball_bowler = False
            bowler_runs_for_stats = extras + runs # Nb(1) + runs(R)
        elif e_type_norm in ["bye", "legbye"]:
            batsman_runs_for_stats = 0
            counts_as_ball_batsman = True
            counts_as_ball_bowler = True
            bowler_runs_for_stats = 0
        elif e_type_norm == "penalty":
            batsman_runs_for_stats = 0
            counts_as_ball_batsman = False
            counts_as_ball_bowler = False
            bowler_runs_for_stats = 0
        else:
            bowler_runs_for_stats = runs

        if counts_as_ball_bowler:
            total_balls_by_innings[innings_ball] += 1

        update_batsman_stats(match_id, batsman, batsman_runs_for_stats, counts_as_ball_batsman)
        update_bowler_stats(match_id, bowler, bowler_runs_for_stats, counts_as_ball_bowler, wicket)
    
        # Optional: Sync scoreboard live inside the loop if necessary, but manual aggregation below is safer.
        
    # Finally, recalculate match_scores from ball_by_ball with exact aggregation
    for inn in [1, 2]:
        update_scoreboard(match_id, inn)
        
    mysql.connection.commit()

# ======================
# FINAL ENDPOINTS
# ======================

@routes.route("/match/edit_score", methods=["POST"])
def edit_score():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 200
        
        match_id = data.get("match_id")
        innings = data.get("innings", 1)
        new_runs = int(data.get("runs", 0))
        new_wickets = int(data.get("wickets", 0))
        # Parse overs X.Y into total balls
        overs_str = str(data.get("overs", "0.0"))
        parts = overs_str.split('.')
        new_balls = int(parts[0]) * 6 + (int(parts[1]) if len(parts) > 1 else 0)
    
        cur = mysql.connection.cursor()
        # 1. Calculate the exact score WITHOUT adjustments from ball_by_ball
        # Runs & wickets
        cur.execute("SELECT SUM(runs + extras), SUM(wicket) FROM ball_by_ball WHERE match_id=%s AND innings=%s", (match_id, innings))
        agg = cur.fetchone()
        db_runs = int(agg[0] or 0) if agg else 0
        db_wickets = int(agg[1] or 0) if agg else 0
        
        # Balls
        cur.execute("SELECT COUNT(*) FROM ball_by_ball WHERE match_id=%s AND innings=%s AND extras_type NOT IN ('wide','no_ball', 'penalty')", (match_id, innings))
        db_balls = cur.fetchone()[0] or 0
    
        # 2. Compute the REQUIRED adjustment so that db_value + adj_value = new_value
        adj_runs = new_runs - db_runs
        adj_wickets = new_wickets - db_wickets
        adj_balls = new_balls - db_balls
    
        # 3. Update the match_scores row with the new adjustment and the new totals
        crr = float(round((new_runs * 6) / new_balls, 2)) if new_balls > 0 else 0.0
        
        # Make sure to update BOTH adj values and the actual cached final totals
        cur.execute("""
            UPDATE match_scores
            SET runs=%s, wickets=%s, total_balls=%s, balls=%s, overs=%s, crr=%s,
                adj_runs=%s, adj_wickets=%s, adj_balls=%s
            WHERE match_id=%s AND innings=%s
        """, (new_runs, new_wickets, new_balls, new_balls, overs_str, crr, adj_runs, adj_wickets, adj_balls, match_id, innings))
        
        mysql.connection.commit()
        
        return jsonify({
            "status": "success",
            "message": "Score updated successfully via adjustment",
            "new_score": {
                "runs": new_runs,
                "wickets": new_wickets,
                "overs": overs_str
            }
        })
    except Exception as e:
        print("ERROR IN EDIT_SCORE:", str(e))
        return jsonify({"status": "error", "message": "Server error: " + str(e)}), 200

@routes.route("/match/refresh_score", methods=["POST", "OPTIONS"])
@routes.route("/match/recompute_score/v1", methods=["POST", "OPTIONS"])
@routes.route("/match/sync_score", methods=["POST", "OPTIONS"])
def force_refresh_score():
    """Nuclear sync for any match/innings. Rebuilds from ball_by_ball ground truth."""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    try:
        data = request.get_json(force=True)
        match_id = int(data.get("match_id"))
        innings = int(data.get("innings", 1))
        
        print(f"[SYNC] Force refreshing Match {match_id} Innings {innings}")
        cur = mysql.connection.cursor()
        
        # 1. Reset all manual adjustments to force use of ball_by_ball data
        cur.execute("""
            UPDATE match_scores
            SET adj_runs=0, adj_wickets=0, adj_balls=0
            WHERE match_id=%s AND innings=%s
        """, (match_id, innings))
        
        # 2. Synchronize metadata
        cur.execute("UPDATE matches SET current_innings=%s WHERE id=%s", (innings, match_id))
        mysql.connection.commit()
        
        # 3. Perform a full atomic rebuild of all aggregated stats
        rebuild_match_state(match_id)
        
        return jsonify({
            "status": "success", 
            "message": f"Match {match_id} score synchronized perfectly from database."
        })
    except Exception as e:
        print(f"[ERROR] Sync failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@routes.route("/match/undo/<match_id>", methods=["DELETE"])
def undo_ball(match_id):
    cur = mysql.connection.cursor()
    
    # 1. Find last ball info
    cur.execute("""
        SELECT id, innings, runs, extras, wicket, extras_type, extras_runs, striker, non_striker, bowler
        FROM ball_by_ball 
        WHERE match_id=%s 
        ORDER BY id DESC LIMIT 1
    """, (match_id,))
    last_ball = cur.fetchone()
    
    if not last_ball:
        return jsonify({"status":"error", "message":"No balls to undo"}), 400
        
    ball_id, innings, b_runs, b_extras, b_wicket, b_extra_type, b_extra_runs, b_striker, b_non_striker, b_bowler = last_ball
    
    # 2. Restore current players state from this ball's initial state
    print(f"[DEBUG] Undo: Restoring players to state BEFORE ball {ball_id}: {b_striker}/{b_non_striker} by {b_bowler}")
    cur.execute("UPDATE current_players SET striker=%s, non_striker=%s, bowler=%s WHERE match_id=%s", 
                (b_striker or "Not Set", b_non_striker or "Not Set", b_bowler or "Not Set", match_id))

    # 3. Delete the ball
    cur.execute("DELETE FROM ball_by_ball WHERE id=%s", (ball_id,))
    
    # 4. Revert current_innings if necessary
    cur.execute("SELECT innings FROM ball_by_ball WHERE match_id=%s ORDER BY id DESC LIMIT 1", (match_id,))
    remaining_ball = cur.fetchone()
    current_active_innings = remaining_ball[0] if remaining_ball else 1
    cur.execute("UPDATE matches SET current_innings=%s WHERE id=%s", (current_active_innings, match_id))
    
    # 5. Full Atomic Commit BEFORE Rebuild
    mysql.connection.commit()
    
    # 6. Recompute all stats from historical ball-by-ball (Ground Truth)
    rebuild_match_state(match_id)
    
    return jsonify({"status":"success","message":"Last ball undone and stats synchronized."})

@routes.route("/match/score/<int:match_id>", methods=["GET"])
def scoreboard(match_id):
    innings = int(request.args.get("innings", 1))
    update_scoreboard(match_id, innings)
    cur = mysql.connection.cursor()
    cur.execute("SELECT runs,wickets,balls,crr FROM match_scores WHERE match_id=%s AND innings=%s",(match_id,innings))
    score = cur.fetchone() or (0,0,0,0)
    
    # Compute overs string from balls
    ov = score[2] // 6
    rm = score[2] % 6
    overs_str = f"{ov}.{rm}"
    
    return jsonify({"runs":score[0],"wickets":score[1],"overs":overs_str,"crr":score[3],"balls":score[2]})

@routes.route("/match/state/<int:match_id>", methods=["GET"])
def match_state(match_id):
    user_id = request.args.get("user_id")
    
    try:
        cur = mysql.connection.cursor()
        # Fetch current active innings and toss info from match metadata
        cur.execute("SELECT team_a, team_b, venue, format, current_innings, toss_winner, toss_decision FROM matches WHERE id=%s", (match_id,))
        meta = cur.fetchone()
        if not meta:
            return jsonify({"error": "Match not found"}), 404
            
        current_active_innings = meta[4]
        # Use query param if provided, else use persisted state
        innings = request.args.get("innings", current_active_innings)
    except Exception as e:
        return jsonify({
            "error": "Database connection failed",
            "details": str(e)
        }), 500
    
    # 1. Main Score (Fetching adjustments)
    cur.execute("SELECT runs, wickets, overs, balls, crr, total_balls, adj_runs, adj_wickets, adj_balls FROM match_scores WHERE match_id=%s AND innings=%s", (match_id, innings))
    score_row = cur.fetchone()
    adj_runs = int(score_row[6] or 0) if score_row else 0
    adj_wickets = int(score_row[7] or 0) if score_row else 0
    adj_balls = int(score_row[8] or 0) if score_row else 0
    
    # 2. Get Out Players
    cur.execute("SELECT DISTINCT batsman FROM ball_by_ball WHERE match_id=%s AND innings=%s AND wicket=1", (match_id, innings))
    out_rows = cur.fetchall()
    out_players = [r[0] for r in out_rows]

    
    # 1.5 NUCLEAR SYNC: Count actual balls from ball_by_ball to be absolutely sure
    cur.execute("""
        SELECT COUNT(*) FROM ball_by_ball 
        WHERE match_id=%s AND innings=%s 
        AND (extras_type IS NULL OR LOWER(TRIM(extras_type)) NOT IN ('wide', 'no_ball', 'no ball', 'penalty'))
    """, (match_id, innings))
    actual_balls = (cur.fetchone()[0] or 0) + adj_balls
    print(f"DEBUG: Actual ball count (including adjustments): {actual_balls} (from bb: {actual_balls - adj_balls}, adj: {adj_balls})")

    
    teamA_name, teamB_name, venue, match_format = meta[0], meta[1], meta[2], meta[3]
    # 3. Current Players (Striker, Non-Striker, Bowler)
    cur.execute("SELECT striker, non_striker, bowler FROM current_players WHERE match_id=%s", (match_id,))
    players = cur.fetchone()

    # Determine batting and bowling teams for the REQUESTED innings
    batting_team_name = None
    bowling_team_name = None
    toss_winner = meta[5] # 'Team A' or 'Team B'
    toss_decision = meta[6] # 'Batting' or 'Bowling'

    # Check if we can determine from current players
    if players and (players[0] != "Not Set" or players[1] != "Not Set"):
        active_player = players[0] if players[0] != "Not Set" else players[1]
        cur.execute("SELECT team_name FROM match_players WHERE match_id=%s AND player_name=%s", (match_id, active_player))
        p_team = cur.fetchone()
        if p_team:
            batting_team_name = p_team[0]
            bowling_team_name = teamB_name if batting_team_name == teamA_name else teamA_name

    # Fallback to toss logic if not determined by players or if viewing non-active innings
    if not batting_team_name or int(innings) != current_active_innings:
        # Innings 1 evaluation
        if (toss_winner == 'Team A' and toss_decision == 'Batting') or \
           (toss_winner == 'Team B' and toss_decision == 'Bowling'):
            # Team A bats first
            first_batting = teamA_name
            first_bowling = teamB_name
        else:
            # Team B bats first
            first_batting = teamB_name
            first_bowling = teamA_name

        # Determine for requested innings
        target_innings = int(innings)
        if target_innings == 1:
            batting_team_name = first_batting
            bowling_team_name = first_bowling
        else:
            batting_team_name = first_bowling
            bowling_team_name = first_batting
    
    # 4. Detailed Stats for Current Players
    striker_stats = (0, 0)
    non_striker_stats = (0, 0)
    bowler_stats = (0, 0, 0)
    
    if players:
        striker, non_striker, bowler = players
        
        # PERFECT STRIKER STATS
        cur.execute("""
            SELECT SUM(runs), COUNT(*) 
            FROM ball_by_ball 
            WHERE match_id=%s AND innings=%s AND batsman=%s 
            AND (extras_type IS NULL OR extras_type != 'wide')
        """, (match_id, innings, striker))
        s_res = cur.fetchone()
        if s_res and s_res[1] > 0: striker_stats = s_res
        
        # PERFECT NON-STRIKER STATS
        cur.execute("""
            SELECT SUM(runs), COUNT(*) 
            FROM ball_by_ball 
            WHERE match_id=%s AND innings=%s AND batsman=%s 
            AND (extras_type IS NULL OR extras_type != 'wide')
        """, (match_id, innings, non_striker))
        ns_res = cur.fetchone()
        if ns_res and ns_res[1] > 0: non_striker_stats = ns_res
        
        # PERFECT BOWLER STATS
        cur.execute("""
            SELECT SUM(runs + extras), SUM(wicket), COUNT(*)
            FROM ball_by_ball 
            WHERE match_id=%s AND innings=%s AND bowler=%s
            AND (extras_type IS NULL OR LOWER(TRIM(extras_type)) NOT IN ('wide', 'no_ball', 'no ball', 'penalty'))
        """, (match_id, innings, bowler))
        b_res = cur.fetchone()
        if b_res:
            b_runs_conc = b_res[0] or 0
            b_wkts = b_res[1] or 0
            b_balls = b_res[2] or 0
            b_overs_str = f"{b_balls // 6}.{b_balls % 6}"
            bowler_stats = (b_runs_conc, b_wkts, b_overs_str)

    # Map results with fallback to perfect calculation from ball_by_ball
    cur.execute("""
        SELECT SUM(runs + extras), SUM(CASE WHEN wicket = 1 THEN 1 ELSE 0 END)
        FROM ball_by_ball WHERE match_id=%s AND innings=%s
    """, (match_id, innings))
    bb = cur.fetchone()
    
    db_runs = (int(bb[0] or 0) if bb else 0) + adj_runs
    db_wickets = (int(bb[1] or 0) if bb else 0) + adj_wickets
    
    db_total_balls = actual_balls
    db_balls = actual_balls
    db_overs = f"{actual_balls // 6}.{actual_balls % 6}"
    db_crr = float((db_runs * 6.0) / actual_balls) if actual_balls > 0 else 0.0

    res = {
        "runs": db_runs,
        "wickets": db_wickets,
        "overs": db_overs,
        "balls": db_total_balls,
        "crr": db_crr,


        "team_a": meta[0] if (meta and meta[0]) else "Team A",
        "team_b": meta[1] if (meta and meta[1]) else "Team B",
        "venue": meta[2] if (meta and meta[2]) else "Venue",
        "format": meta[3] if (meta and meta[3]) else "T20",
        "striker": players[0] if (players and players[0]) else "Not Set",
        "striker_runs": striker_stats[0] if striker_stats[0] is not None else 0,
        "striker_balls": striker_stats[1] if striker_stats[1] is not None else 0,
        "non_striker": players[1] if (players and players[1]) else "Not Set",
        "non_striker_runs": non_striker_stats[0] if non_striker_stats[0] is not None else 0,
        "non_striker_balls": non_striker_stats[1] if non_striker_stats[1] is not None else 0,
        "bowler": (players[2] if (players and players[2]) else "Not Set"),
        "bowler_runs": int(bowler_stats[0] or 0),
        "bowler_wickets": int(bowler_stats[1] or 0),
        "bowler_overs": str(bowler_stats[2]) if (bowler_stats and bowler_stats[2] is not None) else "0.0",
        "current_innings": current_active_innings,
        "batting_team": (batting_team_name or "").strip(),
        "bowling_team": (bowling_team_name or "").strip(),
        "out_players": out_players,
        "inn1_runs": 0,
        "inn1_wickets": 0
    }
    
    # 4.5 Stats for alternative innings (Target/Innings 1)
    if int(innings) == 2:
        cur.execute("SELECT runs, wickets FROM match_scores WHERE match_id=%s AND innings=1", (match_id,))
        inn1 = cur.fetchone()
        if inn1:
            res["inn1_runs"] = int(inn1[0] or 0)
            res["inn1_wickets"] = int(inn1[1] or 0)
    
    # 4.6 Last Bowler Tracking
    cur.execute("SELECT bowler FROM ball_by_ball WHERE match_id=%s AND innings=%s ORDER BY id DESC LIMIT 1", (match_id, innings))
    lb_row = cur.fetchone()
    res["last_bowler"] = lb_row[0] if lb_row else None
    
    # 4.7 Over End Flag
    res["over_ended"] = (actual_balls % 6 == 0 and actual_balls > 0)
    
    # GROUND TRUTH OVERRIDE: Prioritize live double-checked sums
    runs_from_scores = score_row[0] if score_row else 0
    if db_runs > (runs_from_scores or 0):
        res["runs"] = db_runs
        res["wickets"] = db_wickets
        # total_balls calculation for overs display
        ov_count = actual_balls // 6
        ov_rem = actual_balls % 6
        res["overs"] = f"{ov_count}.{ov_rem}"
        res["balls"] = actual_balls
        if actual_balls > 0:
            res["crr"] = round((db_runs * 6) / actual_balls, 2)
        print(f"[FIX] match_state override: set runs to {db_runs} from ball_by_ball")
    
    # 5. Predictions (Real-time sync)
    try:
        pred_data = generate_full_prediction(match_id, innings=innings)
        res["predictions"] = pred_data
    except Exception as e:
        print(f"DEBUG: Prediction generation failed for match {match_id}: {e}")
        res["predictions"] = None

    return jsonify(res)

@routes.route("/match/new_batsman", methods=["POST"])
def set_new_batsman():
    data = request.json
    match_id = data["match_id"]
    new_player = (data["new_player"] or "").strip()
    role = data.get("role", "striker") # 'striker' or 'non_striker'
    
    cur = mysql.connection.cursor()
    if role == "striker":
        cur.execute("UPDATE current_players SET striker=%s WHERE match_id=%s", (new_player, match_id))
    else:
        cur.execute("UPDATE current_players SET non_striker=%s WHERE match_id=%s", (new_player, match_id))
    
    # Initialize stats for new batsman if they don't exist
    cur.execute("SELECT id FROM batsman_stats WHERE match_id=%s AND player_name=%s", (match_id, new_player))
    if not cur.fetchone():
        cur.execute("INSERT INTO batsman_stats(match_id,player_name,runs,balls,fours,sixes) VALUES(%s,%s,0,0,0,0)", (match_id, new_player))
    
    mysql.connection.commit()
    return jsonify({"status": "success", "message": f"New {role} set"})

@routes.route("/match/swap_strikers", methods=["POST"])
def swap_strikers():
    data = request.json
    match_id = data.get("match_id")
    
    if not match_id:
        return jsonify({"error": "match_id missing"}), 400
        
    cur = mysql.connection.cursor()
    cur.execute("SELECT striker, non_striker FROM current_players WHERE match_id=%s", (match_id,))
    res = cur.fetchone()
    
    if not res:
        return jsonify({"error": "Match current players not found"}), 404
        
    s, ns = res
    cur.execute("UPDATE current_players SET striker=%s, non_striker=%s WHERE match_id=%s", (ns, s, match_id))
    mysql.connection.commit()
    
    return jsonify({"status": "success", "message": "Strikers swapped"})

@routes.route("/user/score", methods=["POST"])
def user_score():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO user_scores(user_id,match_id,runs,wickets,overs) VALUES(%s,%s,%s,%s,%s)",(data["user_id"],data["match_id"],data["runs"],data["wickets"],data["overs"]))
    mysql.connection.commit()
    return jsonify({"message":"Saved"})

@routes.route("/predict", methods=["POST"])
def predict():
    """Live match prediction based on trained model.pkl."""
    data = request.json
    match_id = data.get("match_id")
    if not match_id:
        return jsonify({"win_probability": 50.0, "error": "Missing match_id"}), 400
        
    cur = mysql.connection.cursor()
    # 1. Fetch match format and innings
    cur.execute("SELECT current_innings, format FROM matches WHERE id=%s", (match_id,))
    match_info = cur.fetchone()
    if not match_info:
        return jsonify({"win_probability": 50.0, "error": "Match not found"}), 404
        
    inn = match_info[0]
    total_overs = int(match_info[1] or 20)
    total_balls = total_overs * 6
    
    # 2. Fetch current scores
    cur.execute("SELECT runs, wickets, total_balls FROM match_scores WHERE match_id=%s AND innings=%s", (match_id, inn))
    score_data = cur.fetchone()
    runs = score_data[0] if score_data else 0
    wickets = score_data[1] if score_data else 0
    balls_bowled = score_data[2] if score_data else 0
    
    # 3. Fetch target for 2nd innings
    target = 0
    if inn == 2:
        cur.execute("SELECT runs FROM match_scores WHERE match_id=%s AND innings=1", (match_id,))
        target_row = cur.fetchone()
        target = (target_row[0] if target_row else 0) + 1
        
    # 4. Feature Vector: [innings, runs, wickets, balls_bowled, target, total_match_balls]
    features = np.array([[inn, runs, wickets, balls_bowled, target, total_balls]])
    
    global model
    if model is None:
        load_match_model()
        
    if model is None:
        return jsonify({"win_probability": 50.0, "error": "Model missing"}), 500
        
    try:
        prob = model.predict_proba(features)[0][1]
        return jsonify({"win_probability": round(prob * 100, 2)})
    except Exception as e:
        print(f"[ERROR] Prediction failed for match {match_id}: {e}")
        return jsonify({"win_probability": 50.0, "error": str(e)})

@routes.route("/matches", methods=["GET"])
def get_all_matches():
    """Resolve the frontend 404 by providing a unified matches endpoint."""
    user_id = request.args.get("user_id")
    if user_id in [None, "null", "undefined", ""]:
        user_id = None
    print(f"[DEBUG] Fetching all matches for user_id: {user_id}")
    cur = mysql.connection.cursor()
    # Fetch upcoming, live, and completed matches
    cur.execute("""
        SELECT id, team_a, team_b, venue, status, winner, format 
        FROM matches 
        WHERE %s IS NULL OR user_id = %s OR user_id IS NULL 
        ORDER BY id DESC
    """, (user_id, user_id))
    matches = cur.fetchall()
    
    result = []
    for m in matches:
        result.append({
            "match_id": m[0],
            "team_a": m[1],
            "team_b": m[2],
            "venue": m[3],
            "status": m[4],
            "winner": m[5],
            "format": m[6]
        })
    return jsonify(result)

@routes.route("/prediction/save", methods=["POST"])
def save_prediction():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO predictions(user_id,match_id,win_probability) VALUES(%s,%s,%s)",(data["user_id"],data["match_id"],data["probability"]))
    mysql.connection.commit()
    return jsonify({"message":"Prediction stored"})

def generate_full_prediction(match_id, innings=None):
    try:
        cur = mysql.connection.cursor()
        
        # Identify the current active innings from matches table if not provided
        if not innings:
            cur.execute("SELECT current_innings FROM matches WHERE id=%s", (match_id,))
            m_row = cur.fetchone()
            innings = int(m_row[0]) if m_row and m_row[0] else 1
        else:
            innings = int(innings)
        
        cur.execute("SELECT runs, wickets, balls, crr FROM match_scores WHERE match_id=%s AND innings=%s", (match_id, innings))
        s = cur.fetchone()
        
        if not s:
            # Default starting state
            runs, wickets, balls, crr = 0.0, 0, 0, 0.0
        else:
            runs, wickets, balls, crr = float(s[0] or 0), int(s[1] or 0), int(s[2] or 0), float(s[3] or 0)
        
        # Calculate overs as float for ML model (X.Y)
        overs_val = float(f"{balls // 6}.{balls % 6}")

        cur.execute("SELECT team_a, team_b, format FROM matches WHERE id=%s", (match_id,))
        m = cur.fetchone()
        teamA_name, teamB_name, match_format = m if m else ("Team A", "Team B", "20")
        
        # Determine max balls based on format (which is now number of overs)
        try:
            # Extract first numeric part (handles "20" or "20 Overs")
            total_overs = int(str(match_format).split()[0])
            max_balls = total_overs * 6
        except (ValueError, TypeError, IndexError):
            if "T10" in str(match_format).upper(): 
                total_overs = 10
                max_balls = 60
            elif "ODI" in str(match_format).upper(): 
                total_overs = 50
                max_balls = 300
            else: 
                total_overs = 20
                max_balls = 120 

        # Determine Format-based Par RR for more accurate baseline
        if total_overs <= 10: par_rr = 9.5
        elif total_overs <= 20: par_rr = 8.5
        else: par_rr = 5.5

        # 0. Recent Momentum (Last 12 and 24 balls for trend analysis)
        cur.execute("SELECT runs, extras, wicket FROM ball_by_ball WHERE match_id=%s AND innings=%s ORDER BY id DESC LIMIT 24", (match_id, innings))
        all_recent_balls = cur.fetchall()
        
        # Recent Momentum (Casting for type safety)
        last_12 = all_recent_balls[:12]
        recent_runs_12 = float(sum(float(b[0] or 0) + float(b[1] or 0) for b in last_12))
        recent_wickets_12 = int(sum(1 for b in last_12 if b[2] == 1))
        recent_crr_12 = float((recent_runs_12 * 6.0) / max(1, len(last_12)) if len(last_12) > 0 else crr)

        recent_runs_24 = float(sum(float(b[0] or 0) + float(b[1] or 0) for b in all_recent_balls))
        recent_wickets_24 = int(sum(1 for b in all_recent_balls if b[2] == 1))
        recent_crr_24 = float((recent_runs_24 * 6.0) / max(1, len(all_recent_balls)) if len(all_recent_balls) > 0 else crr)

        # 1. Player Impact Analysis
        cur.execute("SELECT striker, non_striker, bowler FROM current_players WHERE match_id=%s", (match_id,))
        cp_state = cur.fetchone()
        striker_name, non_striker_name, current_bowler_name = cp_state if cp_state else ("Not Set", "Not Set", "Not Set")
        
        s_id, ns_id, b_id = get_player_id(striker_name), get_player_id(non_striker_name), get_player_id(current_bowler_name)
        s_career = get_player_career_stats(s_id) or {"avg": 25, "sr": 120}
        ns_career = get_player_career_stats(ns_id) or {"avg": 25, "sr": 120}
        cb_career = get_player_career_stats(b_id) or {"eco": 8.5}
        
        def get_match_stats(p_name):
            if not p_name or p_name == "Not Set": return None
            cur.execute("SELECT bat_runs, bat_balls, bowl_runs_conceded, bowl_balls, bowl_wickets FROM match_players WHERE match_id=%s AND player_name=%s", (match_id, p_name))
            return cur.fetchone()

        s_match, ns_match, cb_match = get_match_stats(striker_name), get_match_stats(non_striker_name), get_match_stats(current_bowler_name)
        
        s_match_runs = float(s_match[0] if s_match else 0)
        s_match_balls = float(s_match[1] if s_match else 0)
        s_match_sr = (s_match_runs * 100.0 / max(1, s_match_balls)) if s_match_balls > 0 else 0.0
        cb_match_eco = (float(cb_match[2] if cb_match else 0) * 6.0 / max(1, float(cb_match[3] if cb_match else 0))) if (cb_match and cb_match[3]) else 8.5

        settled_bonus = 0.0
        if s_match_runs > 15 and s_match_sr > 130: settled_bonus += 4.5
        if (float(ns_match[0] if ns_match else 0)) > 15: settled_bonus += 2.5

        bowler_pressure = 0.0
        if float(cb_match[3] if cb_match else 0) > 6 and cb_match_eco < 6.5: bowler_pressure = 5.0
        if int(cb_match[4] if cb_match else 0) > 1: bowler_pressure += 3.0

        batting_factor = ((float(s_career.get("sr", 120)) + float(ns_career.get("sr", 120))) / 240.0) * (1.0 + (settled_bonus / 100.0))
        bowling_factor = (8.5 / max(4.0, float(cb_career.get("eco", 8.5)))) * (1.0 + (bowler_pressure / 100.0))
        player_impact = (batting_factor * 3.0) - (bowling_factor * 3.0)

        # 2. Win Probability calculation
        progress_pct = float(balls) / float(max_balls) if max_balls > 0 else 0.0
        balls_left = max(0, int(max_balls) - int(balls))

        if balls == 0:
            prob = 50.0 + player_impact
        else:
            current_rr = float(runs) / max(0.1, float(balls) / 6.0)
            if innings == 1:
                rr_diff = current_rr - float(par_rr)
                weight = 0.3 + (0.7 * progress_pct)
                momentum_adj = (recent_crr_24 - current_rr) * 2.5 - (float(recent_wickets_12) * 10)
                prob_calc = 50 + (rr_diff * 4 - (int(wickets) * 8)) * weight + momentum_adj + player_impact
                prob = min(98, max(2, prob_calc))
            else:
                cur.execute("SELECT runs FROM match_scores WHERE match_id=%s AND innings=1", (match_id,))
                target_row = cur.fetchone()
                target = float(target_row[0] + 1) if target_row else 150.0
                runs_needed = target - float(runs)
                if balls_left <= 0:
                    prob = 100 if float(runs) >= target else 0
                else:
                    req_rr = (runs_needed * 6.0) / float(balls_left)
                    rr_gap = current_rr - req_rr
                    momentum_impact = (recent_crr_12 - req_rr) * 4.5 - (float(recent_wickets_12) * 18)
                    wicket_impact = (10 - int(wickets)) / 10.0
                    prob_calc = 50 + (rr_gap * 12) * progress_pct * wicket_impact + momentum_impact + player_impact
                    heuristic_prob = min(98, max(2, prob_calc))
                    
                    if 'model' in globals() and model is not None:
                        try:
                            ml_features = np.array([[float(runs_needed), float(balls_left), int(wickets)]])
                            ml_prob = model.predict_proba(ml_features)[0][1] * 100
                            ml_weight = 0.3 + (0.2 * progress_pct)
                            final_prob = ((1.0 - ml_weight) * heuristic_prob) + (ml_weight * ml_prob)
                            prob = min(98, max(2, final_prob))
                        except:
                            prob = heuristic_prob
                    else:
                        prob = heuristic_prob

        # 3. Projections & Range logic
        overs_left = float(balls_left) / 6.0
        if innings == 1:
            if balls == 0: projected = float(total_overs) * float(par_rr)
            else:
                adj_rr = (current_rr * 0.6) + (recent_crr_24 * 0.4)
                projected = float(runs) + (float(balls_left) * (adj_rr / 6.0))
            total_label, total_range = "Projected Total", f"{int(projected-5)}-{int(projected+10)}"
        else:
            cur.execute("SELECT runs FROM match_scores WHERE match_id=%s AND innings=1", (match_id,))
            t_row = cur.fetchone()
            target_val = int(t_row[0] + 1) if t_row else 0
            total_label, total_range = "Target", str(target_val)

        # 4. Batsman Forecast
        batsman_data = []
        overs_left_full = float(balls_left) / 6.0  # exact overs remaining

        for pname, pstats, match_s, share in [
            (striker_name, s_career, s_match, 0.6),
            (non_striker_name, ns_career, ns_match, 0.4)
        ]:
            cur.execute(
                "SELECT bat_runs, bat_balls, bat_fours, bat_sixes "
                "FROM match_players WHERE match_id=%s AND player_name=%s",
                (match_id, (pname or "").strip())
            )
            b = cur.fetchone()
            if b:
                r_val   = float(b[0] or 0)
                b_val   = float(b[1] or 0)
                f_val   = int(b[2] or 0)
                s_val   = int(b[3] or 0)

                # Current match strike rate (fallback to career SR when few balls faced)
                m_sr = (r_val * 100.0 / max(1.0, b_val)) if b_val > 5 else float(pstats.get("sr", 120))
                effective_sr = (float(pstats.get("sr", 120)) * 0.4) + (m_sr * 0.6)

                # Balls this batsman will realistically face in remaining overs
                batsman_balls_left = overs_left_full * 6.0 * share

                # Projected additional runs = balls_facing * (effective_sr / 100)
                projected_extra = int(batsman_balls_left * (effective_sr / 100.0))

                final_predicted = int(r_val) + projected_extra

                # Boundary % — guard against 0 runs
                if r_val > 0:
                    boundary_pct = int(round(((f_val * 4 + s_val * 6) / r_val) * 100))
                    boundary_pct = min(boundary_pct, 100)
                else:
                    boundary_pct = 0

                # Out risk: base on wickets fallen + pressure from few overs left
                # More overs left → lower immediate pressure; fewer overs → higher aggression risk
                base_risk = 8 + int(wickets) * 3
                # Pressure increases non-linearly as overs run out
                overs_pressure = int((1.0 - min(1.0, overs_left_full / max(1.0, float(total_overs)))) * 30)
                # Batsman who is settled (many balls faced) is less likely to get out rashly
                settled_discount = min(15, int(b_val / 6))  # up to -15% if very settled
                out_risk = max(5, min(95, base_risk + overs_pressure - settled_discount))

                batsman_data.append({
                    "name": pname,
                    "final_runs": final_predicted,
                    "boundary_percent": boundary_pct,
                    "out_risk": out_risk
                })
            else:
                # Batsman not found in match_players — use career defaults
                career_sr = float(pstats.get("sr", 120)) if pstats else 120.0
                batsman_balls_left = overs_left_full * 6.0 * share
                projected_extra = int(batsman_balls_left * (career_sr / 100.0))
                base_risk = 8 + int(wickets) * 3
                overs_pressure = int((1.0 - min(1.0, overs_left_full / max(1.0, float(total_overs)))) * 30)
                batsman_data.append({
                    "name": (pname or "Unknown"),
                    "final_runs": projected_extra,
                    "boundary_percent": 0,
                    "out_risk": max(5, min(95, base_risk + overs_pressure))
                })

        # Final Team Mapping
        cur.execute("SELECT team_name FROM match_players WHERE match_id=%s AND player_name=%s", (match_id, striker_name))
        tp_row = cur.fetchone()
        is_team_a_batting = (tp_row[0].strip().upper() == teamA_name.strip().upper()) if tp_row else True
        winA, winB = (prob, 100.0 - prob) if is_team_a_batting else (100.0 - prob, prob)

        return {
            "current_state": {"runs": int(runs), "wickets": int(wickets), "balls": int(balls)},
            "winner_prediction": {teamA_name: round(float(winA), 1), teamB_name: round(float(winB), 1)},
            "team_names": {"a": teamA_name, "b": teamB_name},
            "next_over": {"runs": round(recent_crr_12 * min(1.0, overs_left) * 1.15, 1)},
            "next_5_overs": {"runs": round(recent_crr_24 * min(5.0, overs_left) * 1.1, 1)},
            "wicket_probability": min(100, round((int(wickets) / 10 * 100) + 12 + recent_wickets_12 * 5)),
            "projected_score": {"range": total_range, "label": total_label},
            "batsman_forecast": batsman_data
        }
    except Exception as e:
        print(f"[FATAL] Global prediction engine failure: {e}")
        # Fallback to avoid breaking frontend completely
        return {
            "current_state": {"runs": 0, "wickets": 0, "balls": 0},
            "winner_prediction": {"Team A": 50.0, "Team B": 50.0},
            "team_names": {"a": "Team A", "b": "Team B"},
            "projected_score": {"range": "Calculated Offline", "label": "Status"},
            "error": str(e)
        }


@routes.route("/match/scorecard/<int:match_id>")
def get_perfect_scorecard(match_id):
    try:
        cur = mysql.connection.cursor()
        
        # 1. Fetch Match & Team info
        cur.execute("SELECT team_a, team_b, toss_winner, toss_decision FROM matches WHERE id=%s", (match_id,))
        m_row = cur.fetchone()
        
        if not m_row:
            return jsonify({"error": "Match not found"}), 404


        team_a_name, team_b_name, toss_w, toss_d = m_row
        team_a_name = (team_a_name or "Team A").strip()
        team_b_name = (team_b_name or "Team B").strip()

        # 2. Fetch All Recorded Stats from ball_by_ball (Ground Truth)
        cur.execute("""
            SELECT batsman, innings, SUM(runs), COUNT(*), SUM(CASE WHEN runs=4 THEN 1 ELSE 0 END), SUM(CASE WHEN runs=6 THEN 1 ELSE 0 END)
            FROM ball_by_ball 
            WHERE match_id=%s 
            AND (extras_type IS NULL OR extras_type != 'wide')
            GROUP BY batsman, innings
        """, (match_id,))
        bat_rows = cur.fetchall()
        
        cur.execute("""
            SELECT bowler, innings, SUM(runs + extras), SUM(wicket), COUNT(*)
            FROM ball_by_ball 
            WHERE match_id=%s
            AND (extras_type IS NULL OR LOWER(TRIM(extras_type)) NOT IN ('wide', 'no_ball', 'no ball', 'penalty'))
            GROUP BY bowler, innings
        """, (match_id,))
        bowl_rows = cur.fetchall()

        # 3. Fetch all match players to include DNBs
        cur.execute("SELECT player_name, team_name FROM match_players WHERE match_id=%s", (match_id,))
        players = cur.fetchall()
        player_teams = {p[0]: p[1] for p in players}

        scorecard = {
            "team_a": {"batting": [], "bowling": [], "name": team_a_name},
            "team_b": {"batting": [], "bowling": [], "name": team_b_name}
        }

        # Helper to find team key
        def get_team_key(p_name):
            t = player_teams.get(p_name, "")
            return "team_a" if (t.strip().upper() == team_a_name.upper()) else "team_b"

        # Organize Batting
        recorded_batsmen = set()
        for p_name, innings, runs, balls, fours, sixes in bat_rows:
            key = get_team_key(p_name)
            scorecard[key]["batting"].append({
                "player_name": p_name,
                "innings": innings,
                "runs": int(runs or 0),
                "balls": int(balls or 0),
                "fours": int(fours or 0),
                "sixes": int(sixes or 0),
                "status": "out"
            })
            recorded_batsmen.add(p_name)

        # Add DNBs
        for p_name, t_name in players:
            if p_name not in recorded_batsmen:
                key = get_team_key(p_name)
                scorecard[key]["batting"].append({
                    "player_name": p_name,
                    "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "status": "DNB"
                })

        # Organize Bowling
        for p_name, innings, r_conc, wickets, balls in bowl_rows:
            key = get_team_key(p_name)
            opp_key = "team_b" if key == "team_a" else "team_a"
            scorecard[opp_key]["bowling"].append({
                "player_name": p_name,
                "innings": innings,
                "overs": f"{int(balls)//6}.{int(balls)%6}",
                "runs": int(r_conc or 0),
                "wickets": int(wickets or 0),
                "maidens": 0
            })

        return jsonify(scorecard)

    except Exception as e:
        print(f"SCORECARD ERROR: {e}")
        return jsonify({"error": str(e)}), 500


@routes.route("/user/favorite_team", methods=["POST"])
def favorite_team():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO user_favorite_teams(user_id,team_name) VALUES(%s,%s)",(data["user_id"],data["team"]))
    mysql.connection.commit()
    return jsonify({"message":"Team added"})

@routes.route("/user/profile/<user_id>", methods=["GET"])
def profile(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT name,email FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    if not user: return jsonify({"error":"User not found"}), 404
    return jsonify({"name": user[0], "email": user[1]})

@routes.route("/match/end", methods=["POST"])
def end_match():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("UPDATE matches SET status='completed', winner=%s WHERE id=%s",(data["winner"],data["match_id"]))
    mysql.connection.commit()
    
    # Refresh the global prediction cache with the new completed match data
    refresh_global_aggregates()
    
    return jsonify({"message":"Match completed"})

@routes.route("/match/change_bowler", methods=["POST"])
def change_bowler():
    data = request.json
    match_id = data["match_id"]
    bowler = (data["bowler"] or "").strip()
    cur = mysql.connection.cursor()
    cur.execute("UPDATE current_players SET bowler=%s WHERE match_id=%s",(bowler,match_id))
    # Initialize stats for new bowler if they don't exist
    cur.execute("SELECT id FROM bowler_stats WHERE match_id=%s AND player_name=%s",(match_id, bowler))
    if not cur.fetchone():
        cur.execute("INSERT INTO bowler_stats(match_id,player_name,overs,maidens,runs,wickets,balls) VALUES(%s,%s,0,0,0,0,0)",(match_id,bowler))
    mysql.connection.commit()
    return jsonify({"message":"Bowler updated"})

@routes.route("/match/update_innings", methods=["POST"])
def update_innings():
    data = request.json
    match_id = data.get("match_id")
    innings = data.get("innings")
    if not match_id or not innings:
        return jsonify({"error":"Missing match_id or innings"}), 400
    
    cur = mysql.connection.cursor()
    
    # 1. Update the match innings marker
    cur.execute("UPDATE matches SET current_innings=%s WHERE id=%s", (innings, match_id))
    
    # 2. Ensure match_scores row exists for the newly started innings
    cur.execute("SELECT id FROM match_scores WHERE match_id=%s AND innings=%s", (match_id, innings))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO match_scores(match_id,innings,runs,wickets,overs,crr,total_balls) VALUES(%s,%s,0,0,'0.0',0,0)", 
            (match_id, innings)
        )
        
    # 3. Clear the current players to trigger the new setup prompt 
    cur.execute("UPDATE current_players SET striker=NULL, non_striker=NULL, bowler=NULL WHERE match_id=%s", (match_id,))
    
    # 4. Trigger scoreboard sync for new innings
    update_scoreboard(match_id, innings)
    
    mysql.connection.commit()
    return jsonify({"message": "Innings updated successfully"})


@routes.route("/match/last6/<int:match_id>", methods=["GET"])
def last_six_balls(match_id):
    innings = int(request.args.get("innings", 1))
    cur = mysql.connection.cursor()
    cur.execute("SELECT runs, extras, wicket, extras_type FROM ball_by_ball WHERE match_id=%s AND innings=%s ORDER BY id DESC LIMIT 6",(match_id, innings))
    balls = cur.fetchall()
    result = []
    for b in balls[::-1]:
        runs, extras, wicket, ext_type = b
        if wicket == 1: result.append("W")
        elif ext_type == "wide": result.append(f"{runs+extras}Wd" if (runs+extras) > 1 else "Wd")
        elif ext_type == "no_ball": result.append(f"{runs+extras}Nb" if (runs+extras) > 1 else "Nb")
        elif ext_type == "bye": result.append(f"{runs+extras}B")
        elif ext_type == "legbye": result.append(f"{runs+extras}L")
        elif ext_type == "penalty": result.append(f"{runs+extras}P")
        else: result.append(str(runs))
    return jsonify(result)

@routes.route("/matches/completed", methods=["GET"])
def completed_matches():
    user_id = request.args.get("user_id")
    if user_id in [None, "null", "undefined", ""]:
        user_id = None
    print(f"[DEBUG] Fetching completed matches for user_id: {user_id}")
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, team_a, team_b, venue, winner, format FROM matches WHERE status='completed' AND (%s IS NULL OR user_id=%s OR user_id IS NULL) ORDER BY id DESC",(user_id, user_id))
    matches = cur.fetchall()
    result = []
    for m in matches:
        result.append({
            "match_id": m[0],
            "team_a": m[1],
            "team_b": m[2],
            "venue": m[3],
            "winner": m[4],
            "format": m[5]
        })
    return jsonify(result)

# Global Cache for Prediction Aggregates
GLOBAL_TEAM_WR = {}
GLOBAL_PLAYER_PROFILES = {}

def refresh_global_aggregates():
    """Build historical lookup for teams and players across all completed matches."""
    global GLOBAL_TEAM_WR, GLOBAL_PLAYER_PROFILES
    try:
        cur = mysql.connection.cursor()
        # 1. Team Win Rates
        cur.execute("SELECT team_a, team_b, winner FROM matches WHERE status='completed'")
        matches = cur.fetchall()
        teams = {}
        for m in matches:
            t_a, t_b, win = m
            for t in [t_a, t_b]:
                if t not in teams: teams[t] = {'p': 0, 'w': 0}
                teams[t]['p'] += 1
            if win in teams: teams[win]['w'] += 1
        GLOBAL_TEAM_WR = {t: (v['w']/v['p'] if v['p'] > 0 else 0.5) for t, v in teams.items()}

        # 2. Player SR and Wkt Rate
        cur.execute("SELECT player_name, bat_runs, bat_balls, bowl_balls, bowl_wickets FROM match_players")
        players = cur.fetchall()
        p_stats = {}
        for p in players:
            name, br, bb, ob, ow = p
            if name not in p_stats: p_stats[name] = {'br': 0, 'bb': 0, 'ob': 0, 'ow': 0}
            p_stats[name]['br'] += br or 0
            p_stats[name]['bb'] += bb or 0
            p_stats[name]['ob'] += ob or 0
            p_stats[name]['ow'] += ow or 0
        
        GLOBAL_PLAYER_PROFILES = {}
        GLOBAL_PLAYER_PROFILES = {name: {'sr': (v['br']/v['bb']*100) if v['bb']>0 else 100.0, 'wkt': (v['ob']/v['ow']) if v['ow']>0 else 100.0} for name, v in p_stats.items()}
        print("[INFO] Aggregates refreshed.")
    except Exception as e: print(f"[ERROR] Aggregation error: {e}")

@routes.route("/match/predictions/<int:match_id>", methods=["GET"])
def get_match_predictions(match_id):
    """Unified predicted entry point that calls the core prediction engine."""
    innings = request.args.get("innings")
    data = generate_full_prediction(match_id, innings=innings)
    return jsonify(data)
