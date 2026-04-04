import sys
import os
import unittest
from unittest.mock import MagicMock

# Add current dir to path
sys.path.append(os.getcwd())

def test_prediction_logic():
    print("Testing Prediction Logic...")
    try:
        # Mocking Flask and MySQL for a deep dive
        import routes
        print("Import successful.")
        
        # We need a context to run the route
        from flask import Flask
        app = Flask(__name__)
        
        with app.test_request_context():
            # Mock MySQL
            routes.mysql = MagicMock()
            mock_cur = routes.mysql.connection.cursor.return_value
            
            # Setup mock data for Match 153
            # m_data: team_a, team_b, inn, fmt, toss_w, toss_d
            mock_cur.fetchone.side_effect = [
                ("max", "jack", 1, 5, "max", "bat"), # match data
                (5,), # format
                (30, 0, 12), # score sum
                None, # target (inn 1)
                ("max",), # bat_team
                [], # recent balls
                ("Krishna", "Ajith", "Bowler") # current players
            ]
            
            print("Invoking get_match_predictions(153)...")
            response = routes.get_match_predictions(153)
            print(f"Response: {response.get_json()}")
            
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_prediction_logic()
