from flask import Flask
from routes import suggest_bp  # Import the Blueprint for routes

app = Flask(__name__)
app.register_blueprint(suggest_bp)  # Register the routes blueprint

if __name__ == "__main__":
    app.run(debug=True)
