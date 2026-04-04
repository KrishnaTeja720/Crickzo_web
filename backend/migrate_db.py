try:
    import mysql.connector as mysql_adapter
except ImportError:
    try:
        import MySQLdb as mysql_adapter
    except ImportError:
        print("No mysql adapter found (mysql-connector or mysqlclient)")
        exit(1)

try:
    conn = mysql_adapter.connect(
        host='localhost',
        user='root',
        passwd='' if hasattr(mysql_adapter, 'connect') else '', # Handle field name difference
        db='crickai_db' if hasattr(mysql_adapter, 'connect') else 'crickai_db'
    )
    # Actually MySQLdb and mysql.connector use different arg names
    # Let's try to be more specific
    if 'MySQLdb' in str(mysql_adapter):
         conn = mysql_adapter.connect(host='localhost', user='root', passwd='', db='crickai_db')
    else:
         conn = mysql_adapter.connect(host='localhost', user='root', password='', database='crickai_db')
    cur = conn.cursor()
    print("Checking if dismissal_type exists...")
    cur.execute("DESCRIBE ball_by_ball")
    columns = [row[0] for row in cur.fetchall()]
    
    if 'dismissal_type' not in columns:
        print("Adding dismissal_type column...")
        cur.execute("ALTER TABLE ball_by_ball ADD COLUMN dismissal_type VARCHAR(50) DEFAULT NULL")
        conn.commit()
        print("Column added successfully!")
    else:
        print("dismissal_type column already exists.")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
