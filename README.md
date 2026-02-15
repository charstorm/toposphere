# Toposphere

Personal note-taking API with email-based authentication.

## Features

- Email/password authentication with token auth
- User registration and login
- Full CRUD for personal notes
- Search notes by title or content
- Users can only access their own notes

## Setup

```bash
# Install dependencies (uses uv)
uv sync

# Activate virtual environment
source .venv/bin/activate

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login and get token |

### Notes (requires authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notes/` | List notes (use `?search=` to filter) |
| POST | `/api/notes/` | Create note |
| GET | `/api/notes/<id>/` | Retrieve note |
| PUT | `/api/notes/<id>/` | Update note |
| PATCH | `/api/notes/<id>/` | Partial update |
| DELETE | `/api/notes/<id>/` | Delete note |

## Running Tests

```bash
python manage.py test
```

## Code Quality

```bash
./check_all.sh  # Runs ruff format, ruff check, mypy --strict
```
