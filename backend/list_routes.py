from app import app
import os
print(f"APP FILE: {os.path.abspath(__file__)}")

routes_list = []
for rule in app.url_map.iter_rules():
    routes_list.append(f"{rule.endpoint} ({rule.rule}) - {list(rule.methods)}")

for r in sorted(routes_list):
    print(r)
