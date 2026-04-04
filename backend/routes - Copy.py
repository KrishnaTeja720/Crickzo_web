from flask import Blueprint, request, jsonify
from db import mysql
from flask_bcrypt import Bcrypt
import random
import smtplib
from email.mime.text import MIMEText
import joblib
import numpy as np

routes = Blueprint("routes", __name__)
bcrypt = Bcrypt()

# ======================
# LOAD ML MODEL
# ======================

try:
    model = joblib.load("ml_model/win_predictor.pkl")
except:
    model = None

#===================================
#   score engine
#==================================
def update_scoreboard(match_id):

    cur = mysql.connection.cursor()

    # total runs
    cur.execute("""
        SELECT SUM(runs + extras)
        FROM ball_by_ball
        WHERE match_id=%s
    """,(match_id,))
    runs = cur.fetchone()[0] or 0

    # wickets
    cur.execute("""
        SELECT COUNT(*)
        FROM ball_by_ball
        WHERE match_id=%s AND wicket=1
    """,(match_id,))
    wickets = cur.fetchone()[0]

    # balls
    cur.execute("""
        SELECT COUNT(*)
        FROM ball_by_ball
        WHERE match_id=%s
    """,(match_id,))
    balls = cur.fetchone()[0]

    overs = balls // 6
    balls_rem = balls % 6
    overs = float(f"{overs}.{balls_rem}")

    if overs > 0:
        crr = round((runs * 6) / balls,2) if balls > 0 else 0
    else:
        crr = 0

    # check existing row
    cur.execute(
        "SELECT id FROM match_scores WHERE match_id=%s",
        (match_id,)
    )

    exists = cur.fetchone()

    if exists:

        cur.execute("""
        UPDATE match_scores
        SET runs=%s, wickets=%s, overs=%s, crr=%s
        WHERE match_id=%s
        """,(runs,wickets,overs,crr,match_id))

    else:

        cur.execute("""
        INSERT INTO match_scores(match_id,runs,wickets,overs,crr)
        VALUES(%s,%s,%s,%s,%s)
        """,(match_id,runs,wickets,overs,crr))

    mysql.connection.commit()

def new_batsman(match_id,new_player):

    cur=mysql.connection.cursor()

    cur.execute("""
    UPDATE current_players
    SET striker=%s
    WHERE match_id=%s
    """,(new_player,match_id))

    mysql.connection.commit()
#=================================================
#UPDATE BATSMAN
#=================================================
def update_batsman(match_id,runs,wicket):

    cur=mysql.connection.cursor()

    cur.execute(
        "SELECT striker,non_striker FROM current_players WHERE match_id=%s",
        (match_id,)
    )

    players=cur.fetchone()

    striker=players[0]

    # update runs
    cur.execute("""
    UPDATE batsman_stats
    SET runs=runs+%s,
        balls=balls+1,
        fours=fours + CASE WHEN %s=4 THEN 1 ELSE 0 END,
        sixes=sixes + CASE WHEN %s=6 THEN 1 ELSE 0 END
    WHERE match_id=%s AND player_name=%s
    """,(runs,runs,runs,match_id,striker))

    # strike rotation
    if runs % 2 == 1:
        cur.execute("""
        UPDATE current_players
        SET striker=non_striker,
            non_striker=striker
        WHERE match_id=%s
        """,(match_id,))

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

    hashed=bcrypt.generate_password_hash(new_password).decode("utf-8")

    cur=mysql.connection.cursor()

    cur.execute(
        "UPDATE users SET password=%s WHERE email=%s",
        (hashed,email)
    )

    mysql.connection.commit()

    return jsonify({"message":"Password updated"})
#==========================================
# MATCH DETAILS
#==========================================
@routes.route("/match/details/<match_id>", methods=["GET"])
def match_details(match_id):

    cur = mysql.connection.cursor()

    # match info
    cur.execute("""
    SELECT team_a,team_b,venue,format
    FROM matches
    WHERE id=%s
    """,(match_id,))

    match = cur.fetchone()

    # safety if match not found
    if not match:
        return jsonify({"error":"Match not found"}),404

    # score
    cur.execute("""
    SELECT runs,wickets,overs,crr
    FROM match_scores
    WHERE match_id=%s
    """,(match_id,))

    score = cur.fetchone()

    return jsonify({

        "team_a": match[0],
        "team_b": match[1],
        "venue": match[2],
        "format": match[3],

        "runs": score[0] if score else 0,
        "wickets": score[1] if score else 0,
        "overs": score[2] if score else 0,
        "crr": score[3] if score else 0

    })

# ======================
# CREATE MATCH
# ======================

@routes.route("/match/create", methods=["POST"])
def create_match():

    data=request.json

    cur=mysql.connection.cursor()

    cur.execute("""
    INSERT INTO matches(team_a,team_b,format,venue,toss_winner,pitch_type,weather,status)
    VALUES(%s,%s,%s,%s,%s,%s,%s,'live')
    """,
    (
        data["team_a"],
        data["team_b"],
        data["format"],
        data["venue"],
        data["toss"],
        data["pitch"],
        data["weather"]
    ))

    mysql.connection.commit()

    return jsonify({"message":"Match created"})


# ======================
# LIVE MATCHES
# ======================
@routes.route("/matches/live", methods=["GET"])
def live_matches():

    cur = mysql.connection.cursor()

    cur.execute("""
    SELECT m.id,m.team_a,m.team_b,m.venue,
           s.runs,s.wickets,s.overs,s.crr
    FROM matches m
    LEFT JOIN match_scores s ON m.id = s.match_id
    WHERE m.status='live'
    ORDER BY m.id DESC
    """)

    rows = cur.fetchall()

    result=[]

    for r in rows:

        result.append({
            "match_id":r[0],
            "team_a":r[1],
            "team_b":r[2],
            "venue":r[3],
            "runs":r[4] if r[4] else 0,
            "wickets":r[5] if r[5] else 0,
            "overs":r[6] if r[6] else 0,
            "crr":r[7] if r[7] else 0
        })

    return jsonify(result)
# ======================
# ADD PLAYERS
# ======================

@routes.route("/match/add_players", methods=["POST"])
def add_players():

    data=request.json

    match_id=data["match_id"]
    team=data["team"]
    players=data["players"]

    cur=mysql.connection.cursor()

    for p in players:

        cur.execute(
            "INSERT INTO players(match_id,team,player_name) VALUES(%s,%s,%s)",
            (match_id,team,p)
        )

    mysql.connection.commit()

    return jsonify({"message":"Players added"})

# ======================
# FETCH PLAYERS
# ======================

@routes.route("/match/players/<match_id>", methods=["GET"])
def get_players(match_id):

    cur = mysql.connection.cursor()

    cur.execute("""
    SELECT team,player_name
    FROM players
    WHERE match_id=%s
    """,(match_id,))

    rows = cur.fetchall()

    teamA=[]
    teamB=[]

    for r in rows:

        if r[0]=="A":
            teamA.append(r[1])
        else:
            teamB.append(r[1])

    return jsonify({
        "teamA":teamA,
        "teamB":teamB
    })

# ======================
# START MATCH
# ======================

@routes.route("/match/start", methods=["POST"])
def start_match():

    data = request.json

    match_id = data.get("match_id")
    striker = data.get("striker")
    non_striker = data.get("non_striker")
    bowler = data.get("bowler")

    if not match_id or not striker or not non_striker or not bowler:
        return jsonify({"error":"Missing fields"}),400

    cur = mysql.connection.cursor()

    # -----------------------
    # CHECK MATCH EXISTS
    # -----------------------
    cur.execute("SELECT id FROM matches WHERE id=%s",(match_id,))
    match = cur.fetchone()

    if not match:
        return jsonify({"error":"Match not found"}),404


    # -----------------------
    # CLEAR PREVIOUS DATA
    # -----------------------
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
    INSERT INTO bowler_stats(match_id,player_name,overs,maidens,runs,wickets)
    VALUES(%s,%s,0,0,0,0)
    """,(match_id,bowler))


    # -----------------------
    # INITIALIZE SCOREBOARD
    # -----------------------
    cur.execute("""
    INSERT INTO match_scores(match_id,runs,wickets,overs,crr)
    VALUES(%s,0,0,0,0)
    """,(match_id,))


    mysql.connection.commit()

    return jsonify({
        "status":"success",
        "message":"Match started",
        "striker":striker,
        "non_striker":non_striker,
        "bowler":bowler
    })
# =========================
# BATSMAN STATS ENGINE
# =========================

def update_batsman_stats(match_id, batsman, runs, extras):

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT id,runs,balls,fours,sixes
        FROM batsman_stats
        WHERE match_id=%s AND player_name=%s
    """,(match_id,batsman))

    data = cur.fetchone()

    # determine if ball should count
    ball_count = 1 if extras == 0 else 0

    if data:

        batsman_id = data[0]
        runs_old = data[1]
        balls_old = data[2]
        fours_old = data[3]
        sixes_old = data[4]

        # add runs to batsman
        runs_old += runs

        # add ball if valid delivery
        balls_old += ball_count

        # boundaries
        if runs == 4:
            fours_old += 1

        if runs == 6:
            sixes_old += 1

        cur.execute("""
            UPDATE batsman_stats
            SET runs=%s, balls=%s, fours=%s, sixes=%s
            WHERE id=%s
        """,(runs_old,balls_old,fours_old,sixes_old,batsman_id))

    else:

        fours = 1 if runs == 4 else 0
        sixes = 1 if runs == 6 else 0

        cur.execute("""
            INSERT INTO batsman_stats(match_id,player_name,runs,balls,fours,sixes)
            VALUES(%s,%s,%s,%s,%s,%s)
        """,(match_id,batsman,runs,ball_count,fours,sixes))

    mysql.connection.commit()
#=========================================
#  UPDATE BOWLER STATS
#=========================================
def update_bowler_stats(match_id, bowler, runs, extras, wicket):

    cur = mysql.connection.cursor()

    # check if bowler already exists
    cur.execute("""
    SELECT id,runs,wickets,overs
    FROM bowler_stats
    WHERE match_id=%s AND player_name=%s
    """,(match_id,bowler))

    data = cur.fetchone()

    total_runs = runs + extras

    if data:

        bowler_id = data[0]
        runs_old = data[1]
        wickets_old = data[2]

        if wicket == 1:
            wickets_old += 1

        cur.execute("""
        UPDATE bowler_stats
        SET runs=%s, wickets=%s
        WHERE id=%s
        """,(runs_old + total_runs, wickets_old, bowler_id))

    else:

        cur.execute("""
        INSERT INTO bowler_stats(match_id,player_name,runs,wickets)
        VALUES(%s,%s,%s,%s)
        """,(match_id,bowler,total_runs,wicket))

    mysql.connection.commit()

# =========================
# PARTNERSHIP ENGINE
# =========================
def calculate_partnership(match_id):

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
            WHERE match_id=%s AND id>%s
        """,(match_id,last_id))

    else:

        cur.execute("""
            SELECT SUM(runs + extras), COUNT(*)
            FROM ball_by_ball
            WHERE match_id=%s
        """,(match_id,))

    data = cur.fetchone()

    runs = data[0] if data[0] else 0
    balls = data[1] if data[1] else 0

    return {
        "striker": striker,
        "non_striker": non_striker,
        "runs": runs,
        "balls": balls
    }
#=================================================
#   FETCH BOWLER
#=================================================
@routes.route("/match/bowler/<match_id>", methods=["GET"])
def bowler_stats(match_id):

    cur = mysql.connection.cursor()

    cur.execute("""
    SELECT player_name,runs,wickets
    FROM bowler_stats
    WHERE match_id=%s
    """,(match_id,))

    bowlers = cur.fetchall()

    result = []

    for b in bowlers:

        runs = b[1]
        wickets = b[2]

        # balls bowled
        cur.execute("""
        SELECT COUNT(*)
        FROM ball_by_ball
        WHERE match_id=%s AND bowler=%s
        """,(match_id,b[0]))

        balls = cur.fetchone()[0]

        overs = balls // 6
        balls_rem = balls % 6

        overs_display = f"{overs}.{balls_rem}"

        if balls > 0:
            economy = round((runs / (balls/6)),2)
        else:
            economy = 0

        result.append({
            "bowler":b[0],
            "overs":overs_display,
            "runs":runs,
            "wickets":wickets,
            "economy":economy
        })

    return jsonify(result)
#==============================================
# BATS MAN
#==============================================
@routes.route("/match/batsmen/<match_id>", methods=["GET"])
def batsmen(match_id):

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT player_name,runs,balls,fours,sixes
        FROM batsman_stats
        WHERE match_id=%s
    """,(match_id,))

    players = cur.fetchall()

    result=[]

    for p in players:

        runs=p[1]
        balls=p[2]

        if balls>0:
            sr = round((runs/balls)*100,2) if balls>0 else 0
        else:
            sr = 0

        result.append({
            "batsman":p[0],
            "runs":runs,
            "balls":balls,
            "fours":p[3],
            "sixes":p[4],
            "strike_rate":sr 
        })

    return jsonify(result)
#======================================================
#PARTNERSHIP
#=======================================================
@routes.route("/match/partnership/<match_id>")
def partnership(match_id):

    data = calculate_partnership(match_id)

    return jsonify({
        "runs": data["runs"],
        "balls": data["balls"]
    })
#=================================================
#  MATCH BALL
#=====================================================
@routes.route("/match/ball", methods=["POST"])
def ball_input():

    data = request.json

    # -----------------------
    # VALIDATE INPUT
    # -----------------------
    required = ["match_id","innings","batsman","bowler","runs","extras","wicket"]

    for r in required:
        if r not in data:
            return jsonify({"error":f"{r} missing"}),400

    match_id = data["match_id"]
    innings = data["innings"]
    batsman = data["batsman"]
    bowler = data["bowler"]
    runs = int(data["runs"])
    extras = int(data["extras"])
    wicket = int(data["wicket"])

    cur = mysql.connection.cursor()

    # -----------------------
    # CHECK MATCH STATUS
    # -----------------------
    cur.execute("SELECT status FROM matches WHERE id=%s",(match_id,))
    match = cur.fetchone()

    if not match:
        return jsonify({"error":"Match not found"}),404

    if match[0] == "completed":
        return jsonify({"error":"Match already completed"}),400


    # -----------------------
    # CALCULATE NEXT BALL
    # -----------------------
    cur.execute("""
        SELECT over_number, ball_number
        FROM ball_by_ball
        WHERE match_id=%s
        ORDER BY id DESC
        LIMIT 1
    """,(match_id,))

    last = cur.fetchone()

    if last:

        over = last[0]
        ball = last[1]

        if extras in [1,2]:
            next_over = over
            next_ball = ball

        else:
            if ball == 6:
                next_over = over + 1
                next_ball = 1
            else:
                next_over = over
                next_ball = ball + 1

    else:
        next_over = 0
        next_ball = 1


    # -----------------------
    # INSERT BALL
    # -----------------------
    cur.execute("""
    INSERT INTO ball_by_ball(
        match_id,
        innings,
        over_number,
        ball_number,
        batsman,
        bowler,
        runs,
        extras,
        wicket
    )
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """,(
        match_id,
        innings,
        next_over,
        next_ball,
        batsman,
        bowler,
        runs,
        extras,
        wicket
    ))

    mysql.connection.commit()


    # -----------------------
    # UPDATE SCOREBOARD
    # -----------------------
    update_scoreboard(match_id)


    # -----------------------
    # UPDATE BATSMAN STATS
    # -----------------------
    update_batsman_stats(
        match_id,
        batsman,
        runs,
        extras
    )


    # -----------------------
    # UPDATE BOWLER STATS
    # -----------------------
    update_bowler_stats(
        match_id,
        bowler,
        runs,
        extras,
        wicket
    )


    # -----------------------
    # STRIKE ROTATION
    # -----------------------
    if extras == 0 and runs % 2 == 1:

        cur.execute("""
        UPDATE current_players
        SET striker = non_striker,
            non_striker = striker
        WHERE match_id=%s
        """,(match_id,))

        mysql.connection.commit()


    return jsonify({
        "message":"Ball saved",
        "over": next_over,
        "ball": next_ball
    })
# ======================
# UNDO BALL
# ======================

@routes.route("/match/undo/<match_id>", methods=["DELETE"])
def undo_ball(match_id):

    cur=mysql.connection.cursor()

    cur.execute("""
    DELETE FROM ball_by_ball
    WHERE match_id=%s
    ORDER BY id DESC
    LIMIT 1
    """,(match_id,))

    mysql.connection.commit()

    return jsonify({"message":"Last ball removed"})


# ======================
# SCOREBOARD
# ======================

@routes.route("/match/score/<match_id>", methods=["GET"])
def scoreboard(match_id):

    # always recalculate score first
    update_scoreboard(match_id)

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT runs,wickets,overs,crr FROM match_scores WHERE match_id=%s",
        (match_id,)
    )

    score = cur.fetchone()

    if score:
        return jsonify({
            "runs": score[0],
            "wickets": score[1],
            "overs": score[2],
            "crr": score[3]
        })

    return jsonify({"runs":0,"wickets":0,"overs":0,"crr":0})


# ======================
# USER PERSONAL SCORE
# ======================

@routes.route("/user/score", methods=["POST"])
def user_score():

    data=request.json

    cur=mysql.connection.cursor()

    cur.execute("""
    INSERT INTO user_scores(user_id,match_id,runs,wickets,overs)
    VALUES(%s,%s,%s,%s,%s)
    """,
    (
        data["user_id"],
        data["match_id"],
        data["runs"],
        data["wickets"],
        data["overs"]
    ))

    mysql.connection.commit()

    return jsonify({"message":"Saved"})


# ======================
# ML PREDICTION
# ======================

@routes.route("/predict", methods=["POST"])
def predict():

    if model is None:
        return jsonify({"error":"Model missing"})

    data=request.json

    runs=data["runs"]
    wickets=data["wickets"]
    overs=data["overs"]

    features=np.array([[runs,wickets,overs]])

    prob=model.predict_proba(features)[0][1]

    return jsonify({
        "win_probability":round(prob*100,2)
    })


# ======================
# SAVE PREDICTION
# ======================

@routes.route("/prediction/save", methods=["POST"])
def save_prediction():

    data=request.json

    cur=mysql.connection.cursor()

    cur.execute("""
    INSERT INTO predictions(user_id,match_id,win_probability)
    VALUES(%s,%s,%s)
    """,
    (
        data["user_id"],
        data["match_id"],
        data["probability"]
    ))

    mysql.connection.commit()

    return jsonify({"message":"Prediction stored"})
#=======================================
#GENERATE PREDICTION
#=======================================
def generate_full_prediction(match_id):

    cur = mysql.connection.cursor()

    cur.execute("""
    SELECT runs,wickets,overs,crr
    FROM match_scores
    WHERE match_id=%s
    """,(match_id,))

    score = cur.fetchone()

    if not score:
        return None

    runs = score[0]
    wickets = score[1]
    overs = score[2]
    crr = score[3]

    # -----------------------------
    # 1️⃣ Match winner probability
    # -----------------------------
    if model:
        features = np.array([[runs,wickets,overs]])
        prob = model.predict_proba(features)[0][1]*100
    else:
        prob = min(95,max(5,(runs/(overs*10))*100))

    teamA = round(prob)
    teamB = 100 - teamA


    # -----------------------------
    # 2️⃣ Projected score
    # -----------------------------
    remaining = 20 - overs
    projected = runs + (remaining * crr)

    low = int(projected - 10)
    high = int(projected + 10)


    # -----------------------------
    # 3️⃣ Phase analysis
    # -----------------------------
    if overs < 6:
        phase = "Powerplay"
    elif overs < 15:
        phase = "Middle"
    else:
        phase = "Death"


    # -----------------------------
    # 4️⃣ Next over prediction
    # -----------------------------
    next_over = round(crr * 1.2)


    # -----------------------------
    # 5️⃣ Next 5 overs prediction
    # -----------------------------
    next5 = round(crr * 5 * 1.1)


    # -----------------------------
    # 6️⃣ Wicket probability
    # -----------------------------
    wicket_prob = round((wickets/10)*100 + 15)


    # -----------------------------
    # 7️⃣ Partnership forecast
    # -----------------------------
    partnership_runs = round(runs * 0.4)


    # -----------------------------
    # 8️⃣ Batsman forecast
    # -----------------------------
    cur.execute("""
    SELECT player_name,runs,balls
    FROM batsman_stats
    WHERE match_id=%s
    ORDER BY runs DESC
    LIMIT 2
    """,(match_id,))

    batsmen = cur.fetchall()

    batsman_data=[]

    for b in batsmen:

        future_runs = b[1] + int(crr*2)

        batsman_data.append({
            "name":b[0],
            "final_runs":future_runs,
            "boundary_percent":round((b[1]/max(1,b[2]))*100),
            "out_risk":round((wickets+1)*5)
        })


    # -----------------------------
    # 9️⃣ Death overs score
    # -----------------------------
    death_score = round(crr * 5)


    return {

        "winner_prediction":{
            "teamA":teamA,
            "teamB":teamB
        },

        "projected_score":{
            "range":f"{low}-{high}",
            "confidence":78
        },

        "phase_analysis":{
            "phase":phase,
            "death_runs":death_score,
            "confidence":76
        },

        "next_over":{
            "runs":next_over,
            "confidence":72
        },

        "next_5_overs":{
            "runs":next5,
            "confidence":68
        },

        "wicket_probability":wicket_prob,

        "partnership_forecast":{
            "runs":partnership_runs,
            "chance":"35%"
        },

        "batsman_forecast":batsman_data,

        "death_overs_score":{
            "runs":death_score,
            "confidence":76
        }
    }
#===========================
#MATCH PREDICTION
#===========================
@routes.route("/match/predictions/<match_id>")
def match_predictions(match_id):

    data = generate_full_prediction(match_id)

    if not data:
        return jsonify({"error":"Score not available"})

    return jsonify(data)
# ======================
# FAVORITE TEAMS
# ======================

@routes.route("/user/favorite_team", methods=["POST"])
def favorite_team():

    data=request.json

    cur=mysql.connection.cursor()

    cur.execute(
        "INSERT INTO user_favorite_teams(user_id,team_name) VALUES(%s,%s)",
        (data["user_id"],data["team"])
    )

    mysql.connection.commit()

    return jsonify({"message":"Team added"})


# ======================
# USER PROFILE
# ======================

@routes.route("/user/profile/<user_id>", methods=["GET"])
def profile(user_id):

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT name,email FROM users WHERE id=%s",
        (user_id,)
    )

    user = cur.fetchone()

    # check if user exists
    if not user:
        return jsonify({
            "error":"User not found"
        }),404

    return jsonify({
        "name": user[0],
        "email": user[1]
    })


# ======================
# END MATCH
# ======================

@routes.route("/match/end", methods=["POST"])
def end_match():

    data=request.json

    match_id=data["match_id"]
    winner=data["winner"]

    cur=mysql.connection.cursor()

    cur.execute("""
    UPDATE matches
    SET status='completed', winner=%s
    WHERE id=%s
    """,(winner,match_id))

    mysql.connection.commit()

    return jsonify({"message":"Match completed"})
##================================================
# LAST SIX BALLS
#==============================================
@routes.route("/match/last6/<match_id>", methods=["GET"])
def last_six_balls(match_id):

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT runs, extras, wicket
        FROM ball_by_ball
        WHERE match_id=%s
        ORDER BY id DESC
        LIMIT 6
    """, (match_id,))

    balls = cur.fetchall()

    result = []

    for b in balls[::-1]:  # reverse to show oldest → newest

        runs = b[0]
        extras = b[1]
        wicket = b[2]

        if wicket == 1:
            result.append("W")

        elif extras == 1:
            result.append("Wd")

        elif extras == 2:
            result.append("Nb")

        else:
            result.append(str(runs))

    return jsonify(result)
#========================
#MATCH COMPLETED
#==========================
@routes.route("/matches/completed", methods=["GET"])
def completed_matches():

    cur=mysql.connection.cursor()

    cur.execute("""
    SELECT id,team_a,team_b,venue,winner
    FROM matches
    WHERE status='completed'
    ORDER BY id DESC
    """)

    matches=cur.fetchall()

    result=[]

    for m in matches:

        result.append({
            "match_id":m[0],
            "team_a":m[1],
            "team_b":m[2],
            "venue":m[3],
            "winner":m[4]
        })

    return jsonify(result)