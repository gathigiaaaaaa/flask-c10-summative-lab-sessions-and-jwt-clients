"""
routes/auth_routes.py
---------------------
Auth endpoints using Flask-JWT-Extended.

POST   /auth/register  - create a new account
POST   /auth/login     - log in and get a JWT token
GET    /auth/me        - get the current user's profile (JWT required)
DELETE /auth/logout    - confirm logout (client should discard the token)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)

from models import db, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Create a new user account.

    Expected body:
        {
            "username": "alice",
            "email": "alice@example.com",
            "password": "securepassword"
        }

    Returns 201 with the user and a JWT token.
    Returns 400 if fields are missing, the password is too short, or the email/username is taken.
    """
    data = request.get_json()

    missing = [f for f in ("username", "email", "password") if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    username = data["username"].strip()
    email = data["email"].strip().lower()
    password = data["password"]

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400
    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({"error": "Please provide a valid email address."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with that email already exists."}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "That username is already taken."}), 400

    user = User(username=username, email=email)
    user.password = password  # triggers the bcrypt setter in models.py

    db.session.add(user)
    db.session.commit()

    # Log the user in immediately after registering
    access_token = create_access_token(identity=str(user.id))

    return jsonify({"user": user.to_dict(), "access_token": access_token}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Log in with email and password.

    Expected body:
        {
            "email": "alice@example.com",
            "password": "securepassword"
        }

    Returns 200 with the user and a JWT token.
    Returns 400 if fields are missing.
    Returns 401 if the credentials are wrong. The error message is kept generic
    on purpose so an attacker can't tell whether the email exists.
    """
    data = request.get_json()

    missing = [f for f in ("email", "password") if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    email = data["email"].strip().lower()
    password = data["password"]

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password."}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({"user": user.to_dict(), "access_token": access_token}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """
    Get the profile of the currently logged-in user.

    Requires: Authorization: Bearer <token>

    Returns 200 with the user profile.
    Returns 404 if the user was deleted after the token was issued.
    """
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found."}), 404

    return jsonify({"user": user.to_dict()}), 200


@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    """
    Log out.

    JWTs are stateless so the server can't invalidate them. The client
    needs to delete the token on its end. This endpoint just confirms
    the request went through.

    Returns 200.
    """
    return jsonify({"message": "Logged out successfully. Please discard your token."}), 200
