from db import mysql
from flask import Flask
import config
import json
from routes import routes

app = Flask(__name__)
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
mysql.init_app(app)
app.register_blueprint(routes)

def test_scorecard(match_id):
    with app.app_context():
        # Simulate request
        with app.test_client() as client:
            response = client.get(f"/match/scorecard/{match_id}")
            print(f"STATUS: {response.status_code}")
            print("RESPONSE BODY:")
            print(json.dumps(response.get_json(), indent=2))

if __name__ == "__main__":
    import sys
    mid = sys.argv[1] if len(sys.argv) > 1 else "105"
    test_scorecard(mid)
