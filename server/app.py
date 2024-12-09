from flask import Flask
from routes import suggest_bp  # Import the Blueprint for routes
from flask_cors import CORS, cross_origin


app = Flask(__name__)

CORS(app, resources={r"/suggest": {"origins": "http://localhost:3000"}})

app.register_blueprint(suggest_bp)  # Register the routes blueprint

if __name__ == "__main__":
    app.run(debug=True)
