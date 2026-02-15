# Personal Space API - Phase 1 Requirements

## 1. PROJECT OVERVIEW

Personal Space is a REST API backend for personal note-taking. Users can register, authenticate via tokens, and manage their notes through a REST API.

**Tech Stack:**
- Django 5.2 LTS + Django REST Framework 3.16+
- Python 3.11+
- SQLite (default)
- Token authentication (rest_framework.authtoken)

---

## 2. API ENDPOINTS

**Base URL:** http://localhost:8000/api

### 2.1 Authentication Endpoints

#### POST /api/auth/register/
**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "first_name": "John",      // optional
  "last_name": "Doe"          // optional
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "token": "a1b2c3d4...",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Password Validation Rules:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit

**Custom Error Messages:**
- "Password must be at least 8 characters long"
- "Password must contain at least 1 uppercase letter"
- "Password must contain at least 1 lowercase letter"
- "Password must contain at least 1 digit"

#### POST /api/auth/login/
**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "token": "a1b2c3d4...",
  "user_id": 1,
  "email": "user@example.com"
}
```

**Behavior:**
- Return existing token if available (don't create new token on each login)
- Wrong credentials return 400 (not 401)

### 2.2 Notes Endpoints

**Authentication:** All endpoints require `Authorization: Token {token_value}` header

#### GET /api/notes/
**Query Parameters:**
- `page` (optional, default: 1)

**Response (200):**
```json
{
  "count": 42,
  "next": "http://localhost:8000/api/notes/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "My Note",
      "content": "Note content here",
      "created_at": "2025-02-15T10:30:00Z",
      "updated_at": "2025-02-15T14:20:00Z"
    }
  ]
}
```

**Behavior:**
- Page size: 20 items
- Ordering: `updated_at` descending (most recent first)
- Auto-filter by authenticated user only

#### POST /api/notes/
**Request:**
```json
{
  "title": "My Note",
  "content": "Optional content"  // can be empty or omitted
}
```

**Response (201):** Full note object with id and timestamps

**Validation:**
- Title: required, max 200 chars, auto-trim whitespace
- Content: optional, can be empty, max 100KB

#### GET /api/notes/{id}/
**Response (200):** Full note object

**Security:** Return 404 (not 403) when note belongs to another user

#### PATCH /api/notes/{id}/
**Request:** Any combination of title and/or content

**Response (200):** Updated note object with new `updated_at`

#### PUT /api/notes/{id}/
**Request:** Must include title (content optional)

**Response (200):** Updated note object

#### DELETE /api/notes/{id}/
**Response (204):** No content

**Behavior:** Hard delete (permanent removal)

---

## 3. MODELS

### 3.1 User Model
Use Django's built-in `User` model with email as username. No customization needed.

### 3.2 Note Model

**App:** `notes`

```python
class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [models.Index(fields=['-updated_at'])]
```

**Cascade Delete:** When user is deleted, all their notes are auto-deleted.

---

## 4. BUSINESS LOGIC

### 4.1 Authentication Flow

**Registration:**
1. Validate email (unique, valid format)
2. Validate password (custom validator with 4 rules)
3. Hash password using Django's default PBKDF2-SHA256
4. Create user
5. Create auth token (40-char hex string)
6. Return user info + token

**Login:**
1. Authenticate email + password
2. Retrieve or create token
3. Return token + user info

**Token Usage:**
- Format: `Authorization: Token {40-char-hex}`
- No expiration in Phase 1
- No server-side logout endpoint (client deletes token)

### 4.2 Note Access Control

**Core Rule:** Users can ONLY access their own notes

**Implementation:**
- Auto-filter all queries: `Note.objects.filter(user=request.user)`
- Auto-assign user on create (never from request data)
- Return 404 (not 403) for unauthorized access to hide note existence

### 4.3 Data Processing

**Title Handling:**
- Auto-trim leading/trailing whitespace
- Reject if empty after trimming

**Content Handling:**
- Preserve exactly as provided (no trimming)
- Allow empty content

**Timestamps:**
- `created_at`: Set once on creation
- `updated_at`: Auto-update on every save

---

## 5. VALIDATION RULES

### 5.1 Custom Password Validator

**File:** `accounts/validators.py`

Create `PasswordValidator` class checking:
- Length ≥ 8
- Contains uppercase
- Contains lowercase  
- Contains digit

Return specific error messages for each failed rule (see 2.1).

### 5.2 Email Validation
- Use Django's built-in `EmailValidator`
- Enforce uniqueness (case-insensitive)
- Custom error: "A user with this email already exists"

---

## 6. TESTING REQUIREMENTS

### 6.1 Test Organization

**Structure:**
```
accounts/tests/
  - test_validators.py   # Password validator tests
  - test_views.py        # Registration & login API tests

notes/tests/
  - test_models.py       # Note model tests
  - test_views.py        # CRUD API tests
```

### 6.2 Critical Test Cases

**Password Validator:**
- Valid passwords with all requirements pass
- Each missing requirement triggers correct error message

**Authentication API:**
- Register creates user + token, password is hashed
- Duplicate email rejected
- Login returns existing token (not new)
- Wrong credentials return 400

**Notes API:**
- Unauthenticated requests return 401
- List shows only user's notes, ordered by updated_at desc
- Create without title returns 400
- Title auto-trimmed, content preserved
- User cannot access another user's notes (404 response)
- Update changes updated_at, preserves created_at
- Delete performs hard delete

**Pagination:**
- Create 25 notes, verify first page shows 20
- Verify next/previous URLs present

**Multi-User Isolation:**
- Create 2 users with notes
- Verify User A cannot list/retrieve/update/delete User B's notes

### 6.3 Running Tests

```bash
python manage.py test                    # All tests
python manage.py test accounts           # Accounts only
python manage.py test notes.tests.test_views  # Specific file
python manage.py test --keepdb           # Faster reruns
```

---

## 7. OUT OF SCOPE (Phase 1)

- Update user profile via API (use Django admin)
- Change password via API (use Django admin)
- Share notes between users
- Tags/categories
- Search functionality
- Soft delete


===
Coding rules:
When giving python code:
- use type annotation on function args and return
- avoid docstrings
- use helper functions
- keep code modular
- return early when possible
- reduce indented code when possible
- write code that is easy to read and explain
- use idiomatic code
- unless specially asked, don't add try/except blocks
- typing.List, typing.Dict etc are outdated. Use list, dict etc directly for type annotation
- suggest a filename as comment at the end of the code
- comments should handle the "why", not the "what"
- don't mix low level code with high level code
- produce code that is low in cognitive complexity
- use ruff format, ruff check, mypy --strict
- use .venv in the projects basefolder for virtual env
- use uv commands for everyhing