"""
seed.py
-------
Fills the database with sample data for development and testing.

Run with:
    python seed.py

What it does:
    1. Drops and recreates all tables.
    2. Creates 3 users.
    3. Creates 15 journal entries spread across those users.

WARNING: This wipes existing data. Don't run this in production.
"""

from faker import Faker
from app import app
from models import db, User, JournalEntry

fake = Faker()

MOODS = ["happy", "calm", "anxious", "excited", "sad", "motivated", "tired", "grateful", None]

def seed():
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()

        print("Creating all tables...")
        db.create_all()

        print("Seeding users...")

        users = []

        # Predictable accounts so Postman and frontend tests are easy to set up
        alice = User(username="alice", email="alice@example.com")
        alice.password = "password123"
        users.append(alice)

        bob = User(username="bob", email="bob@example.com")
        bob.password = "password123"
        users.append(bob)

        # Third user with random data
        carol_name = fake.user_name()
        carol = User(username=carol_name, email=fake.email())
        carol.password = "password123"
        users.append(carol)

        db.session.add_all(users)
        db.session.commit()
        print(f"  Created {len(users)} users.")

        print("Seeding journal entries...")

        entries = []

        for _ in range(7):
            entries.append(JournalEntry(
                title=fake.sentence(nb_words=5).rstrip("."),
                content=fake.paragraph(nb_sentences=4),
                mood=fake.random_element(MOODS),
                user_id=alice.id,
            ))

        for _ in range(5):
            entries.append(JournalEntry(
                title=fake.sentence(nb_words=5).rstrip("."),
                content=fake.paragraph(nb_sentences=3),
                mood=fake.random_element(MOODS),
                user_id=bob.id,
            ))

        for _ in range(3):
            entries.append(JournalEntry(
                title=fake.sentence(nb_words=4).rstrip("."),
                content=fake.paragraph(nb_sentences=2),
                mood=fake.random_element(MOODS),
                user_id=carol.id,
            ))

        db.session.add_all(entries)
        db.session.commit()
        print(f"  Created {len(entries)} journal entries.")

        print("\nDatabase seeded.")
        print(f"   Users   : {User.query.count()}")
        print(f"   Entries : {JournalEntry.query.count()}")
        print("\nTest credentials (all passwords = 'password123'):")
        for u in User.query.all():
            print(f"   {u.email}")


if __name__ == "__main__":
    seed()
