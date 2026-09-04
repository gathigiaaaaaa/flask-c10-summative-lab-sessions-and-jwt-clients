"""
models.py
---------
Database models for the Productivity API.

User         - stores login credentials and owns journal entries.
JournalEntry - the resource users create. Belongs to one user.
               Deleting a user removes all their entries (cascade).
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    """
    User account.

    Attributes:
        id         - primary key
        username   - unique display name
        email      - unique email used to log in
        _password  - bcrypt hash of the password (never plain text)
        created_at - when the account was created (UTC)
        entries    - this user's journal entries
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)

    # Underscore prefix means: don't set this directly, use the password property
    _password = db.Column("password", db.String(128), nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    entries = db.relationship(
        "JournalEntry",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, plain_text: str):
        """Hash the password before storing it."""
        self._password = bcrypt.generate_password_hash(plain_text).decode("utf-8")

    def check_password(self, plain_text: str) -> bool:
        return bcrypt.check_password_hash(self._password, plain_text)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r}>"


class JournalEntry(db.Model):
    """
    A journal entry belonging to one user.

    Attributes:
        id         - primary key
        title      - short title (required)
        content    - body text (required)
        mood       - optional mood tag, e.g. 'happy', 'anxious'
        created_at - when entry was created (UTC)
        updated_at - when entry was last updated (UTC)
        user_id    - FK to the user who owns this entry
        user       - relationship back to User
    """

    __tablename__ = "journal_entries"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    mood = db.Column(db.String(50), nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="entries")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "mood": self.mood,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "user_id": self.user_id,
        }

    def __repr__(self):
        return f"<JournalEntry id={self.id} title={self.title!r} user_id={self.user_id}>"
