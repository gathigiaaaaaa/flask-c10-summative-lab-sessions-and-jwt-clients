"""
routes/entry_routes.py
----------------------
CRUD endpoints for journal entries.

All routes require a valid JWT. Every query is filtered to the
logged-in user's entries only.

Status codes used:
    401 - missing or invalid JWT (handled by @jwt_required)
    403 - valid JWT but the entry belongs to someone else
    404 - entry not found
    400 - missing or invalid fields

GET    /entries        - list entries, paginated
POST   /entries        - create an entry
GET    /entries/<id>   - get a single entry
PATCH  /entries/<id>   - update an entry
DELETE /entries/<id>   - delete an entry
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import db, JournalEntry

entry_bp = Blueprint("entries", __name__)


def _get_current_user_id() -> int:
    return int(get_jwt_identity())


def _check_ownership(entry: JournalEntry, user_id: int):
    """Returns a 403 response if the entry doesn't belong to user_id, otherwise None."""
    if entry.user_id != user_id:
        return jsonify({"error": "You do not have permission to access this entry."}), 403
    return None


@entry_bp.route("", methods=["GET"])
@jwt_required()
def get_entries():
    """
    Get the logged-in user's entries, newest first.

    Query params:
        page     - page number, default 1
        per_page - results per page, default 10, max 50
    """
    user_id = _get_current_user_id()

    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(50, max(1, int(request.args.get("per_page", 10))))
    except ValueError:
        return jsonify({"error": "page and per_page must be integers."}), 400

    pagination = (
        JournalEntry.query
        .filter_by(user_id=user_id)
        .order_by(JournalEntry.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return jsonify({
        "entries":  [e.to_dict() for e in pagination.items],
        "total":    pagination.total,
        "page":     pagination.page,
        "per_page": pagination.per_page,
        "pages":    pagination.pages,
    }), 200


@entry_bp.route("", methods=["POST"])
@jwt_required()
def create_entry():
    """
    Create a new journal entry.

    Expected body:
        { "title": "...", "content": "...", "mood": "calm" }

    mood is optional. Returns 201 with the new entry.
    """
    user_id = _get_current_user_id()
    data = request.get_json()

    missing = [f for f in ("title", "content") if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    entry = JournalEntry(
        title=data["title"].strip(),
        content=data["content"].strip(),
        mood=data.get("mood", "").strip() or None,
        user_id=user_id,
    )

    db.session.add(entry)
    db.session.commit()

    return jsonify({"entry": entry.to_dict()}), 201


@entry_bp.route("/<int:entry_id>", methods=["GET"])
@jwt_required()
def get_entry(entry_id):
    """Get a single entry by ID. Returns 403 if it belongs to another user."""
    user_id = _get_current_user_id()
    entry = db.session.get(JournalEntry, entry_id)

    if not entry:
        return jsonify({"error": "Entry not found."}), 404

    denied = _check_ownership(entry, user_id)
    if denied:
        return denied

    return jsonify({"entry": entry.to_dict()}), 200


@entry_bp.route("/<int:entry_id>", methods=["PATCH"])
@jwt_required()
def update_entry(entry_id):
    """
    Update a journal entry. Only the fields you send will be changed.
    Accepted fields: title, content, mood.
    """
    user_id = _get_current_user_id()
    entry = db.session.get(JournalEntry, entry_id)

    if not entry:
        return jsonify({"error": "Entry not found."}), 404

    denied = _check_ownership(entry, user_id)
    if denied:
        return denied

    data = request.get_json()
    updated = False

    if "title" in data:
        title = data["title"].strip()
        if not title:
            return jsonify({"error": "Title cannot be empty."}), 400
        entry.title = title
        updated = True

    if "content" in data:
        content = data["content"].strip()
        if not content:
            return jsonify({"error": "Content cannot be empty."}), 400
        entry.content = content
        updated = True

    if "mood" in data:
        # Sending null or an empty string clears the mood field
        entry.mood = data["mood"].strip() if data["mood"] else None
        updated = True

    if not updated:
        return jsonify({"error": "No valid fields provided to update."}), 400

    db.session.commit()
    return jsonify({"entry": entry.to_dict()}), 200


@entry_bp.route("/<int:entry_id>", methods=["DELETE"])
@jwt_required()
def delete_entry(entry_id):
    """Delete an entry. Returns 403 if it belongs to another user."""
    user_id = _get_current_user_id()
    entry = db.session.get(JournalEntry, entry_id)

    if not entry:
        return jsonify({"error": "Entry not found."}), 404

    denied = _check_ownership(entry, user_id)
    if denied:
        return denied

    db.session.delete(entry)
    db.session.commit()

    return jsonify({"message": f"Entry {entry_id} deleted successfully."}), 200
