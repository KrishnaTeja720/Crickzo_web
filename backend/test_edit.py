import requests
import json

import requests
import json

try:
    res = requests.get("http://localhost:5000/match/predictions/71")
    print(res.status_code)
    print(json.dumps(res.json(), indent=2))
except Exception as e:
    print("Error:", e)

