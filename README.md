# Toposphere

Personal note-taking API with email-based authentication.

## Prerequisites

- Python 3.11 or higher
- uv (Python package manager): `pip install uv`

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd toposphere

# Install dependencies and create virtual environment
uv sync

# Activate virtual environment
source .venv/bin/activate
```

### 2. Database Setup

```bash
# Run migrations to create database tables
python manage.py migrate
```

### 3. Start the Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## Testing the API

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

Response:
```json
{
  "token": "abc123def456...",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```

### 2. Create a Note

```bash
curl -X POST http://localhost:8000/api/notes/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -d '{
    "title": "My First Note",
    "content": "This is the content of my note."
  }'
```

### 3. List Your Notes

```bash
curl -X GET http://localhost:8000/api/notes/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### 4. Search Notes

```bash
curl -X GET "http://localhost:8000/api/notes/?search=first" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | Register new user | No |
| POST | `/api/auth/login/` | Login and get token | No |

### Notes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notes/` | List all notes (supports `?search=` query) |
| POST | `/api/notes/` | Create a new note |
| GET | `/api/notes/<id>/` | Retrieve a specific note |
| PUT | `/api/notes/<id>/` | Update a note (full) |
| PATCH | `/api/notes/<id>/` | Partial update |
| DELETE | `/api/notes/<id>/` | Delete a note |

**Note:** All notes endpoints require authentication via `Authorization: Token <token>` header.

## Running Tests

```bash
# Run all tests
python manage.py test

# Run with verbose output
python manage.py test -v 2
```

## Code Quality

Before committing, run the code quality checks:

```bash
./check_all.sh
```

This runs:
- `ruff format` - Code formatting
- `ruff check` - Linting
- `mypy --strict` - Type checking

## Password Requirements

Passwords must have:
- At least 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

## Project Structure

```
toposphere/
├── accounts/          # User authentication app
├── notes/             # Notes CRUD app
├── test/scripts/      # Shell test scripts
├── manage.py          # Django management commands
├── pyproject.toml     # Dependencies and tool config
└── check_all.sh       # Code quality script
```

## Troubleshooting

### Import errors
Make sure the virtual environment is activated:
```bash
source .venv/bin/activate
```

### Database locked
Stop the server and run migrations again:
```bash
python manage.py migrate
```

### Permission denied on check_all.sh
```bash
chmod +x check_all.sh
```
