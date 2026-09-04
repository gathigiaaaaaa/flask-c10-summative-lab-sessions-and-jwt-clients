"""
config.py
---------
Loads app configuration from environment variables.
Keep your .env file out of source control. Copy .env.example to get started.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask session secret
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-secret-key")

    # JWT signing secret
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "fallback-jwt-secret-key")

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///productivity.db")

    # Turns off SQLAlchemy's event system for object modifications (saves memory)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Tokens expire after 1 hour
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
