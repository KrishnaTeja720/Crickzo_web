from db import mysql

def create_tables():

    cur = mysql.connection.cursor()

    # USERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(120) UNIQUE,
        password VARCHAR(255)
    )
    """)

    # OTP
    cur.execute("""
    CREATE TABLE IF NOT EXISTS otp_verification(
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(120),
        otp VARCHAR(10),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # MATCHES
    cur.execute("""
    CREATE TABLE IF NOT EXISTS matches(
        id INT AUTO_INCREMENT PRIMARY KEY,
        team_a VARCHAR(100),
        team_b VARCHAR(100),
        format VARCHAR(20),
        venue VARCHAR(100),
        toss_winner VARCHAR(100),
        pitch_type VARCHAR(50),
        weather VARCHAR(50),
        status VARCHAR(20),
        winner VARCHAR(100)
    )
    """)

    # PLAYERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS players(
        id INT AUTO_INCREMENT PRIMARY KEY,
        match_id INT,
        team VARCHAR(100),
        player_name VARCHAR(100),
        INDEX(match_id)
    )
    """)

    # BALL BY BALL
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ball_by_ball(
        id INT AUTO_INCREMENT PRIMARY KEY,
        match_id INT,
        innings INT,
        over_number INT,
        ball_number INT,
        batsman VARCHAR(100),
        bowler VARCHAR(100),
        runs INT,
        extras INT,
        wicket BOOLEAN,
        INDEX(match_id)
    )
    """)

    # SCOREBOARD
    cur.execute("""
    CREATE TABLE IF NOT EXISTS match_scores(
        id INT AUTO_INCREMENT PRIMARY KEY,
        match_id INT,
        runs INT DEFAULT 0,
        wickets INT DEFAULT 0,
        overs FLOAT DEFAULT 0,
        crr FLOAT DEFAULT 0,
        INDEX(match_id)
    )
    """)

    # BATSMAN STATS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS batsman_stats(
        id INT AUTO_INCREMENT PRIMARY KEY,
        match_id INT,
        player_name VARCHAR(100),
        runs INT DEFAULT 0,
        balls INT DEFAULT 0,
        fours INT DEFAULT 0,
        sixes INT DEFAULT 0,
        INDEX(match_id)
    )
    """)

    # BOWLER STATS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bowler_stats(
        id INT AUTO_INCREMENT PRIMARY KEY,
        match_id INT,
        player_name VARCHAR(100),
        overs FLOAT DEFAULT 0,
        maidens INT DEFAULT 0,
        runs INT DEFAULT 0,
        wickets INT DEFAULT 0,
        INDEX(match_id)
    )
    """)

    # CURRENT PLAYERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS current_players(
        match_id INT PRIMARY KEY,
        striker VARCHAR(100),
        non_striker VARCHAR(100),
        bowler VARCHAR(100)
    )
    """)

    # USER SCORES (missing in your schema)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_scores(
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        match_id INT,
        runs INT,
        wickets INT,
        overs FLOAT
    )
    """)

    # FAVORITE TEAMS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_favorite_teams(
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        team_name VARCHAR(100)
    )
    """)

    # PREDICTIONS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS predictions(
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        match_id INT,
        win_probability FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    mysql.connection.commit()