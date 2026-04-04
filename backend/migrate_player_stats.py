import config
import MySQLdb
import sys

def migrate():
    db = None
    try:
        db = MySQLdb.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            passwd=config.MYSQL_PASSWORD,
            db=config.MYSQL_DB
        )
        cur = db.cursor()
        
        print("Starting migration...")

        # 0. Temporary drop the unique index to allow restructuring
        try:
            print("Checking/Removing match_player_unique index if exists...")
            cur.execute("ALTER TABLE match_players DROP INDEX match_player_unique")
            db.commit()
        except:
            pass # Index might not exist yet

        # 1. Clean up duplicates in match_players (keep only one row per match_id, player_name)
        print("Cleaning up duplicates in match_players...")
        cur.execute("""
            SELECT match_id, player_name, COUNT(*) 
            FROM match_players 
            GROUP BY match_id, player_name 
            HAVING COUNT(*) > 1
        """)
        duplicates = cur.fetchall()
        for mid, name, count in duplicates:
            print(f"  Removing {count-1} duplicate row(s) for '{name}' in match {mid}")
            # Keep the row with the smallest ID
            cur.execute("SELECT id FROM match_players WHERE match_id=%s AND player_name=%s ORDER BY id ASC", (mid, name))
            ids = cur.fetchall()
            ids_to_delete = [str(r[0]) for r in ids[1:]]
            cur.execute(f"DELETE FROM match_players WHERE id IN ({','.join(ids_to_delete)})")
        db.commit()

        # 2. Populate global players table from all unique names
        print("Syncing players to global identity table...")
        cur.execute("SELECT DISTINCT player_name FROM match_players WHERE player_name IS NOT NULL")
        names1 = {r[0] for r in cur.fetchall()}
        cur.execute("SELECT DISTINCT player_name FROM batsman_stats")
        names2 = {r[0] for r in cur.fetchall()}
        cur.execute("SELECT DISTINCT player_name FROM bowler_stats")
        names3 = {r[0] for r in cur.fetchall()}
        
        all_unique_names = names1.union(names2).union(names3)
        print(f"Found {len(all_unique_names)} unique player names.")

        for name in all_unique_names:
            if not name: continue
            cur.execute("INSERT IGNORE INTO players (player_name) VALUES (%s)", (name,))
        
        db.commit()

        # 3. Map player_id in match_players
        print("Linking player_ids in match_players...")
        cur.execute("SELECT player_id, player_name FROM players")
        player_map = {name: pid for pid, name in cur.fetchall()}
        
        cur.execute("SELECT id, player_name FROM match_players")
        mp_rows = cur.fetchall()
        for mp_id, p_name in mp_rows:
            if p_name in player_map:
                cur.execute("UPDATE match_players SET player_id=%s WHERE id=%s", (player_map[p_name], mp_id))
        
        db.commit()

        # 4. Migrate Batting Stats
        print("Migrating batting stats...")
        cur.execute("SELECT match_id, player_name, runs, balls, fours, sixes FROM batsman_stats")
        bat_rows = cur.fetchall()
        for mid, name, runs, balls, fours, sixes in bat_rows:
            pid = player_map.get(name)
            if pid:
                cur.execute("SELECT id FROM match_players WHERE match_id=%s AND player_id=%s", (mid, pid))
                mp_entry = cur.fetchone()
                if mp_entry:
                    cur.execute("""
                        UPDATE match_players 
                        SET bat_runs=%s, bat_balls=%s, bat_fours=%s, bat_sixes=%s 
                        WHERE id=%s
                    """, (runs, balls, fours, sixes, mp_entry[0]))
                else:
                    cur.execute("""
                        INSERT INTO match_players (match_id, player_id, player_name, bat_runs, bat_balls, bat_fours, bat_sixes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (mid, pid, name, runs, balls, fours, sixes))
        
        db.commit()

        # 5. Migrate Bowling Stats
        print("Migrating bowling stats...")
        cur.execute("SELECT match_id, player_name, overs, balls, runs, wickets, maidens FROM bowler_stats")
        bowl_rows = cur.fetchall()
        for mid, name, overs, balls, runs, wickets, maidens in bowl_rows:
            pid = player_map.get(name)
            if pid:
                cur.execute("SELECT id FROM match_players WHERE match_id=%s AND player_id=%s", (mid, pid))
                mp_entry = cur.fetchone()
                if mp_entry:
                    cur.execute("""
                        UPDATE match_players 
                        SET bowl_overs=%s, bowl_balls=%s, bowl_runs_conceded=%s, bowl_wickets=%s, bowl_maidens=%s
                        WHERE id=%s
                    """, (str(overs), balls, runs, wickets, maidens, mp_entry[0]))
                else:
                    cur.execute("""
                        INSERT INTO match_players (match_id, player_id, player_name, bowl_overs, bowl_balls, bowl_runs_conceded, bowl_wickets, bowl_maidens)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (mid, pid, name, str(overs), balls, runs, wickets, maidens))
        
        db.commit()

        # 6. Re-add Unique Index
        print("Applying unique constraint (match_id, player_id)...")
        try:
            cur.execute("ALTER TABLE match_players ADD UNIQUE INDEX match_player_unique (match_id, player_id)")
            db.commit()
        except Exception as e:
            print(f"Warning: Could not add unique index: {e}")

        print("Migration completed successfully!")

    except Exception as e:
        print(f"Migration failed: {e}")
        if db: db.rollback()
    finally:
        if db: db.close()

if __name__ == "__main__":
    migrate()
