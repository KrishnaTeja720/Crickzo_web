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
        user_id INT,
        team_a VARCHAR(100),
        team_b VARCHAR(100),
        format VARCHAR(20),
        venue VARCHAR(100),
        toss_winner VARCHAR(100),
        toss_decision VARCHAR(20),
        current_innings INT DEFAULT 1,
        pitch_type VARCHAR(50),
        weather VARCHAR(50),
        status VARCHAR(20),
        winner VARCHAR(100),
        INDEX(user_id)
    )
    """)

    # MATCH_PLAYERS (Expanded for unified stats and global identity)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS match_players(
        id INT AUTO_INCREMENT PRIMARY KEY,
        match_id INT,
        player_id INT,
        team_name VARCHAR(100),
        player_name VARCHAR(100),
        role VARCHAR(50),
        bat_runs INT DEFAULT 0,
        bat_balls INT DEFAULT 0,
        bat_fours INT DEFAULT 0,
        bat_sixes INT DEFAULT 0,
        bowl_overs VARCHAR(10) DEFAULT '0.0',
        bowl_balls INT DEFAULT 0,
        bowl_maidens INT DEFAULT 0,
        bowl_runs_conceded INT DEFAULT 0,
        bowl_wickets INT DEFAULT 0,
        INDEX(match_id),
        INDEX(player_id)
    )
    """)

    # Ensure new columns exist in match_players (for existing databases)
    cols_to_add = [
        ("player_id", "INT DEFAULT NULL"),
        ("bat_runs", "INT DEFAULT 0"),
        ("bat_balls", "INT DEFAULT 0"),
        ("bat_fours", "INT DEFAULT 0"),
        ("bat_sixes", "INT DEFAULT 0"),
        ("bowl_overs", "VARCHAR(10) DEFAULT '0.0'"),
        ("bowl_balls", "INT DEFAULT 0"),
        ("bowl_maidens", "INT DEFAULT 0"),
        ("bowl_runs_conceded", "INT DEFAULT 0"),
        ("bowl_wickets", "INT DEFAULT 0")
    ]
    for col, definition in cols_to_add:
        try:
            cur.execute(f"SHOW COLUMNS FROM match_players LIKE '{col}'")
            if not cur.fetchone():
                print(f"Adding column {col} to match_players")
                cur.execute(f"ALTER TABLE match_players ADD COLUMN {col} {definition}")
        except Exception as e:
            print(f"Error adding column {col}: {e}")

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
        extras_type VARCHAR(20),
        extras_runs INT,
        wicket BOOLEAN,
        striker VARCHAR(100),
        non_striker VARCHAR(100),
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
        overs VARCHAR(10) DEFAULT '0.0',
        balls INT DEFAULT 0,
        crr FLOAT DEFAULT 0,
        total_balls INT DEFAULT 0,
        innings INT DEFAULT 1,
        adj_runs INT DEFAULT 0,
        adj_wickets INT DEFAULT 0,
        adj_balls INT DEFAULT 0,
        INDEX(match_id)
    )
    """)

    # BATSMAN STATS (Keep for now, but will be deprecated)
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

    # BOWLER STATS (Keep for now, but will be deprecated)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bowler_stats(
        id INT AUTO_INCREMENT PRIMARY KEY,
        match_id INT,
        player_name VARCHAR(100),
        overs FLOAT DEFAULT 0,
        balls INT DEFAULT 0,
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

    # USER SCORES
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

    # PLAYERS ROSTER (Global Identity)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS players(
        player_id INT AUTO_INCREMENT PRIMARY KEY,
        player_name VARCHAR(100),
        team_name VARCHAR(100)
    )
    """)

    # Ensure player_name is UNIQUE for identity mapping
    try:
        cur.execute("SHOW INDEX FROM players WHERE Column_name = 'player_name'")
        if not cur.fetchone():
            print("Adding UNIQUE index to players(player_name)")
            cur.execute("ALTER TABLE players ADD UNIQUE (player_name)")
    except Exception as e:
        print(f"Error adding unique index to players: {e}")

    # Ensure match_id + player_id uniqueness in match_players
    try:
        cur.execute("SHOW INDEX FROM match_players WHERE Key_name = 'match_player_unique'")
        if not cur.fetchone():
            print("Adding UNIQUE index to match_players(match_id, player_id)")
            # First clean up any rows where player_id is NULL to avoid issues if needed
            # Actually, player_id will be NULL for old rows initially
            cur.execute("ALTER TABLE match_players ADD UNIQUE INDEX match_player_unique (match_id, player_id)")
    except Exception as e:
        pass # Might fail if player_ids are still null or duplicates exist; will handle in migration

    mysql.connection.commit()

    mysql.connection.commit()