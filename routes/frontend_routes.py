"""
routes/frontend_routes.py
-------------------------
Routes that match the shape the provided React JWT client expects.

The React client hits these flat paths:
    POST /signup  - create account
    POST /login   - log in
    GET  /me      - get current user (auto-login on refresh)

These sit alongside the existing /auth/* routes. Both work; these exist
specifically so the frontend client works without any changes to it.

Key differences from /auth/* routes:
    - Login accepts username instead of email
    - Signup accepts password_confirmation
    - Token is returned as "token" (not "access_token")
    - Errors are returned as { "errors": ["message"] } (array, not string)
    - /me returns the user object directly (not nested under "user")
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from models import db, User

frontend_bp = Blueprint("frontend", __name__)


@frontend_bp.route("/signup", methods=["POST"])
def signup():
    """
    Create a new account.

    Expected body:
        {
            "username": "alice",
            "password": "secret123",
            "password_confirmation": "secret123"
        }

    Returns 201 with { "token": "...", "user": { ... } } on success.
    Returns 422 with { "errors": [...] } on validation failure.
    """
    data = request.get_json()

    errors = []

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    password_confirmation = data.get("password_confirmation") or ""

    if not username:
        errors.append("Username is required.")
    if not password:
        errors.append("Password is required.")
    if len(password) < 6:
        errors.append("Password must be at least 6 characters.")
    if password != password_confirmation:
        errors.append("Password and confirmation do not match.")
    if User.query.filter_by(username=username).first():
        errors.append("That username is already taken.")

    if errors:
        return jsonify({"errors": errors}), 422

    user = User(username=username, email=f"{username}@placeholder.local")
    user.password = password

    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()}), 201


@frontend_bp.route("/login", methods=["POST"])
def login():
    """
    Log in with username and password.

    Expected body:
        {
            "username": "alice",
            "password": "secret123"
        }

    Returns 200 with { "token": "...", "user": { ... } } on success.
    Returns 401 with { "errors": ["..."] } on bad credentials.
    """
    data = request.get_json()

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"errors": ["Username and password are required."]}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"errors": ["Invalid username or password."]}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()}), 200


@frontend_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """
    Get the currently logged-in user.

    The React client calls this on mount to restore session from localStorage.
    Returns the user object directly (not nested) to match what App.js expects.

    Returns 200 with the user object on success.
    Returns 401 if the token is missing or invalid.
    Returns 404 if the user no longer exists.
    """
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"errors": ["User not found."]}), 404

    # Return user directly - App.js does: r.json().then((user) => setUser(user))
    return jsonify(user.to_dict()), 200
