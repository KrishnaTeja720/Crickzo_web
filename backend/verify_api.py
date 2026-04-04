import requests
import json

try:
    r = requests.get("http://127.0.0.1:5005/match/predictions/148")
    print("API RESPONSE:", r.json())
except Exception as e:
    print("API ERROR:", e)
