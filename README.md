# Toposphere

Personal productivity API with note-taking and todo list management. Features email-based authentication.

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

## API Documentation

Once the server is running, you can access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/api/docs/` - Interactive API explorer with try-it-now functionality
- **ReDoc**: `http://localhost:8000/api/redoc/` - Alternative API documentation interface
- **OpenAPI Schema**: `http://localhost:8000/api/schema/` - Raw OpenAPI 3.0 schema (JSON)

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

### 3. Create a Todo List

```bash
curl -X POST http://localhost:8000/api/todos/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -d '{
    "title": "My Tasks",
    "description": "Things to do"
  }'
```

### 4. Add Items to Todo List

```bash
curl -X POST http://localhost:8000/api/todos/<list_id>/items/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -d '{
    "title": "Buy groceries"
  }'
```

### 5. Mark Item as Complete

```bash
curl -X PATCH http://localhost:8000/api/todos/items/<item_id>/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -d '{
    "is_completed": true
  }'
```

### 6. List Your Notes

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

**Note:** All notes and todos endpoints require authentication via `Authorization: Token <token>` header.

### Todos

Todo items are organized into lists. Each user can have multiple lists, and each list can contain multiple items.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/todos/` | List all todo lists |
| POST | `/api/todos/` | Create a new list |
| GET | `/api/todos/<id>/` | Retrieve a specific list |
| PUT | `/api/todos/<id>/` | Update a list (full) |
| PATCH | `/api/todos/<id>/` | Partial update |
| DELETE | `/api/todos/<id>/` | Delete a list |
| GET | `/api/todos/<list_id>/items/` | List all items in a list |
| POST | `/api/todos/<list_id>/items/` | Create a new item in a list |
| GET | `/api/todos/items/<id>/` | Retrieve a specific item |
| PUT | `/api/todos/items/<id>/` | Update an item (full) |
| PATCH | `/api/todos/items/<id>/` | Partial update (use for marking complete) |
| DELETE | `/api/todos/items/<id>/` | Delete an item |

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
├── todos/             # Todo lists and items app
├── test/scripts/      # Shell test scripts
├── test/scenarios/    # Scenario-based integration tests
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
