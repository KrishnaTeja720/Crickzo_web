from flask import Flask
from flask_cors import CORS
import config
from models import create_tables
from db import mysql
import os
from routes import routes

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# =============================
# DATABASE CONFIG
# =============================

app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
app.config['MYSQL_PORT'] = 3306

mysql.init_app(app)

with app.app_context():
    create_tables()
# =============================
# REGISTER ROUTES
# =============================

app.register_blueprint(routes)

@app.route('/health')
def health_check():
    return {"status": "ok"}, 200

# =============================
# RUN SERVER
# =============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)