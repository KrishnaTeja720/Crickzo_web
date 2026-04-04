from app import app
from routes import generate_full_prediction

with app.app_context():
    try:
        # Test with match 61
        res = generate_full_prediction(61)
        print("Result:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()
