from flask import Flask
from db import mysql
import config

app = Flask(__name__)
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
mysql.init_app(app)

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("DESCRIBE matches")
    columns = cur.fetchall()
    for col in columns:
        print(f"Column: {col[0]}, Type: {col[1]}, Null: {col[2]}, Key: {col[3]}, Default: {col[4]}")
