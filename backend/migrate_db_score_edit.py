from flask import Flask
from flask_mysqldb import MySQL

try:
    import config
except ImportError:
    class config:
        MYSQL_HOST = 'localhost'
        MYSQL_USER = 'root'
        MYSQL_PASSWORD = ''
        MYSQL_DB = 'crickai_db'

app = Flask(__name__)
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql = MySQL(app)

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
        ALTER TABLE match_scores 
        ADD COLUMN adj_runs INT DEFAULT 0,
        ADD COLUMN adj_wickets INT DEFAULT 0,
        ADD COLUMN adj_balls INT DEFAULT 0;
        """)
        mysql.connection.commit()
        print("Columns added successfully!")
    except Exception as e:
        print(f"Error: {e}")
