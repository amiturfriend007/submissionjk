# LuminaLib Backend

Backend service for LuminaLib, implemented with FastAPI + SQLAlchemy async ORM.

## What This Service Does

- Handles authentication (signup, login, profile)
- Manages books (upload, list, update, delete, download/view)
- Tracks borrowing and returns
- Accepts reviews and computes review sentiment asynchronously
- Generates book summaries asynchronously after upload
- Exposes LLM utility endpoints for connectivity checks and chat

## Stack

- Python 3.11
- FastAPI
- SQLAlchemy 2 (async)
- PostgreSQL (primary runtime DB)
- JWT auth (`python-jose`)
- Password hashing (`passlib` with bcrypt/argon2)
- Optional S3-compatible storage (`boto3`)
- Optional Ollama-compatible LLM endpoint (`httpx`)

## Folder Layout

```text
backend/
|-- app/
|   |-- api/
|   |   |-- deps/
|   |   `-- routes/
|   |-- core/
|   |-- db/
|   |-- schemas/
|   |-- services/
|   `-- tasks/
|-- tests/
|-- Dockerfile
|-- pytest.ini
|-- requirements.txt
`-- ROADMAP.md
```

## Quick Start (Local)

1. Go to backend folder:

```bash
cd c:\Amit\submissionjk\backend
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set environment variables (see full table below). Minimum required:

```powershell
$env:DATABASE_URL="postgresql+asyncpg://lumina:lumina@localhost:5432/luminalib"
$env:JWT_SECRET="change-me-now"
```

5. Run API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. Open docs:

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Quick Start (Docker - Backend Only)

From `backend/`:

```bash
docker build -t luminalib-backend .
docker run --rm -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://lumina:lumina@host.docker.internal:5432/luminalib" \
  -e JWT_SECRET="change-me-now" \
  luminalib-backend
```

For full stack (recommended), run from project root:

```bash
docker-compose up --build
```

## Configuration

The app reads settings from environment variables (`app/core/config.py`).

### Required

- `DATABASE_URL` (example: `postgresql+asyncpg://lumina:lumina@db:5432/luminalib`)
- `JWT_SECRET`

### App

- `TITLE` (default: `LuminaLib API`)
- `DEBUG` (default: `false`)

### JWT

- `JWT_ALGORITHM` (default: `HS256`)
- `JWT_EXPIRATION_MINUTES` (default: `1440`)

### Storage

- `STORAGE_BACKEND` (`local` or `s3`, default: `local`)
- `STORAGE_PATH` (default: `./data`)
- `S3_BUCKET`
- `S3_REGION`
- `S3_ACCESS_KEY`
- `S3_SECRET_KEY`
- `S3_ENDPOINT_URL`
- `S3_OBJECT_PREFIX` (default: `books`)

### LLM

- `LLM_PROVIDER` (`local`/`ollama` currently supported)
- `LLM_URL` (default: `http://localhost:11434`)
- `LLM_MODEL` (default: `phi3`)
- `LLM_TIMEOUT_SECONDS` (default: `180`)
- `LLM_MAX_INPUT_CHARS` (default: `12000`)

## API Overview

Base URL: `http://localhost:8000`

### Auth Routes (`/auth`)

- `POST /auth/signup`
- `POST /auth/login`
- `GET /auth/me` (Bearer token required)
- `PUT /auth/me` (Bearer token required)
- `POST /auth/logout`

### Book Routes (`/books`)

- `POST /books/` (multipart upload, supports `.txt` and `.pdf`)
- `GET /books/?page=1`
- `PUT /books/{book_id}`
- `DELETE /books/{book_id}`
- `POST /books/{book_id}/borrow`
- `POST /books/{book_id}/return`
- `POST /books/{book_id}/reviews`
- `GET /books/{book_id}/analysis`
- `POST /books/{book_id}/summary/refresh`
- `GET /books/{book_id}/download`
- `GET /books/{book_id}/view`
- `GET /books/recommendations`

### LLM Utility Routes (`/llm`)

- `GET /llm/status`
- `POST /llm/chat`

## Common API Examples

### 1. Signup

```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret123","full_name":"Test User"}'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret123"}'
```

Response contains `access_token`.

### 3. Upload Book

```bash
curl -X POST http://localhost:8000/books/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -F "title=My Book" \
  -F "author=Author Name" \
  -F "description=Sample description" \
  -F "file=@sample.pdf"
```

### 4. Add Review

```bash
curl -X POST http://localhost:8000/books/1/reviews \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"rating":5,"comment":"Great read."}'
```

## Async Behavior

The API returns quickly and triggers background async tasks for:

- Book summary generation after upload
- Review sentiment scoring after review creation
- Consensus update after review creation

Current implementation uses in-process async tasks (`asyncio.create_task`). For production-grade reliability, move these to a dedicated queue/worker system.

## Storage Backends

### Local (default)

- Files saved under `STORAGE_PATH` with UUID-prefixed names.
- Download/view endpoints serve from local filesystem.

### S3-compatible

- Enable with `STORAGE_BACKEND=s3` and S3 variables.
- Download/view endpoints return presigned URLs when available.

## Testing

From `backend/`:

```bash
pytest
```

Key test modules:

- `tests/test_auth.py`
- `tests/test_books.py`
- `tests/test_storage.py`

`pytest.ini` uses:

- `asyncio_mode = auto`
- `testpaths = tests`
- `python_files = test_*.py`

## Operational Notes

- On startup, tables are created via `Base.metadata.create_all`.
- CORS is currently permissive for local development and includes `*`.
- Alembic is installed but migration flow is not wired into startup.

## Troubleshooting

### App fails at startup with env error

Cause: missing required vars.

Fix: define at least `DATABASE_URL` and `JWT_SECRET`.

### `401 Unauthorized` on protected endpoints

Cause: missing/invalid bearer token.

Fix: login first and send `Authorization: Bearer <token>`.

### `400 Only .txt and .pdf files are supported`

Cause: unsupported extension.

Fix: upload `.txt` or `.pdf` files only.

### LLM endpoints fail or summaries stay pending

Cause: LLM URL/model not reachable.

Fix:

- Verify `LLM_URL` and `LLM_MODEL`
- Check `GET /llm/status`
- Confirm Ollama/service is running

## Next Steps

See [ROADMAP.md](./ROADMAP.md) for production hardening and scaling work.
