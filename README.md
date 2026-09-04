# Productivity App - Journal API

A full-stack journaling app. Users can sign up, log in, and write private journal entries. Nobody can read, edit, or delete another person's entries.

The backend is a Flask REST API using JWT authentication. The frontend is a React app (from the provided JWT client template).

---

## Project Structure

```
flask-c10-summative-lab-sessions-and-jwt-clients/
├── app.py                  # Flask app factory
├── config.py               # Config loaded from .env
├── models.py               # User and JournalEntry models
├── seed.py                 # Seeds the database with test data
├── routes/
│   ├── auth_routes.py      # /auth/* endpoints
│   ├── entry_routes.py     # /entries/* endpoints
│   └── frontend_routes.py  # /signup, /login, /me (matches React client)
├── migrations/             # Alembic migration files
├── client-with-jwt/        # React frontend (JWT version)
├── client-with-sessions/   # React frontend (sessions version, unused)
├── .env.example            # Template for environment variables
├── Pipfile
└── requirements.txt
```

---

## Backend Setup (Flask)

**Requirements:** Python 3.10+

### 1. Create and activate a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or with pipenv:

```bash
pipenv install
pipenv shell
```

### 3. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` with your own values:

```
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=pick-something-random
JWT_SECRET_KEY=pick-something-different-and-random
DATABASE_URL=sqlite:///productivity.db
```

### 4. Run migrations

```bash
flask db upgrade
```

### 5. Seed the database (optional)

```bash
python seed.py
```

Creates 3 users and 15 journal entries. All passwords are `password123`.

Test accounts:
- `alice` / `password123`
- `bob` / `password123`

### 6. Start the Flask server

```bash
flask run --port 5000
```

---

## Frontend Setup (React)

```bash
cd client-with-jwt
npm install
npm start
```

The React app runs on `http://localhost:4000` and proxies API requests to `http://localhost:5000`.

Run the Flask server first, then start React.

---

## API Endpoints

### Auth

| Method | Endpoint  | Auth? | Description                                    |
|--------|-----------|-------|------------------------------------------------|
| POST   | `/signup` | No    | Create an account, returns JWT token           |
| POST   | `/login`  | No    | Log in with username + password, returns token |
| GET    | `/me`     | Yes   | Get the logged-in user (used on page refresh)  |

These match the React client exactly. There are also `/auth/register`, `/auth/login`, `/auth/me`, `/auth/logout` routes for Postman testing.

#### Signup body
```json
{
  "username": "alice",
  "password": "secret123",
  "password_confirmation": "secret123"
}
```

#### Login body
```json
{
  "username": "alice",
  "password": "secret123"
}
```

All protected requests need this header:
```
Authorization: Bearer <token>
```

### Journal Entries

All entry routes require a valid JWT. Each user can only see and edit their own entries.

| Method | Endpoint          | Description                             |
|--------|-------------------|-----------------------------------------|
| GET    | `/entries`        | List your entries, paginated            |
| POST   | `/entries`        | Create a new entry                      |
| GET    | `/entries/<id>`   | Get one entry                           |
| PATCH  | `/entries/<id>`   | Update an entry                         |
| DELETE | `/entries/<id>`   | Delete an entry                         |

#### Entry body (POST / PATCH)
```json
{
  "title": "Morning thoughts",
  "content": "Today was a good day.",
  "mood": "happy"
}
```

`mood` is optional. For PATCH, only send the fields you want to change.

#### Paginated list params
- `page` - page number (default 1)
- `per_page` - results per page, max 50 (default 10)

---

## Security

- Passwords are hashed with bcrypt, never stored plain text.
- JWT tokens expire after 1 hour.
- Every entry route checks that the entry belongs to the logged-in user. Wrong user gets `403`.
- Requests without a token get `401`.

---

## Status Codes

| Code | Meaning                              |
|------|--------------------------------------|
| 200  | OK                                   |
| 201  | Created                              |
| 400  | Bad request, missing or invalid data |
| 401  | Not authenticated                    |
| 403  | Authenticated but wrong user         |
| 404  | Not found                            |
| 422  | Validation error (signup)            |
