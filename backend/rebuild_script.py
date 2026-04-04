from app import app
from routes import rebuild_match_state
import sys

match_id = 56
if len(sys.argv) > 1:
    match_id = int(sys.argv[1])

with app.app_context():
    print(f"Rebuilding match {match_id}...")
    rebuild_match_state(match_id)
    print("Done.")
