from flask import Flask
try:
    from routes import routes
    app = Flask(__name__)
    app.register_blueprint(routes)
    print("Listing Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]")
except Exception as e:
    print(f"Error loading routes: {e}")
