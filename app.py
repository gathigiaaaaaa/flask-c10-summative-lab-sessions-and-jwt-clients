"""
app.py
------
Entry point for the Productivity API.

Run with:
    flask run
    python app.py
"""

from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from config import Config
from models import db, bcrypt


def create_app(config_class=Config):
    """
    App factory. Accepts an optional config so tests can swap it out.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Set up extensions
    db.init_app(app)
    bcrypt.init_app(app)
    Migrate(app, db)
    JWTManager(app)

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.entry_routes import entry_bp
    from routes.frontend_routes import frontend_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(entry_bp, url_prefix="/entries")
    # Flat routes (/signup, /login, /me) for the provided React JWT client
    app.register_blueprint(frontend_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
