import os
from flask import Flask
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    """Application factory for Flask app."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-dev-secret-key')
    app.config['JSON_SORT_KEYS'] = False

    # Register blueprints
    from app.routes import routes
    app.register_blueprint(routes)

    # Automatically initialize tables on start if connection is ready
    try:
        from app.database import init_db
        init_db()
    except Exception as e:
        print(f"Database initialization deferred: {e}")

    return app

