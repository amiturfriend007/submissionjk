# LuminaLib

LuminaLib is a full-stack intelligent library platform built with FastAPI (backend) and Next.js (frontend).

## Core Capabilities

- JWT-based authentication and profile management
- Book upload and metadata management
- Borrow and return workflows
- Review creation with sentiment analysis hooks
- Async task execution for LLM-related processing
- Extensible provider interfaces for storage and LLM backends
- Docker Compose setup for local full-stack development

## Tech Stack

- Backend: FastAPI, SQLAlchemy (async), PostgreSQL
- Frontend: Next.js (App Router), React, TypeScript
- Infrastructure: Docker, Docker Compose
- Testing: Pytest (backend), Jest/RTL (frontend)

## Quick Start

1. Open the project directory:

```bash
cd c:\Amit\submissionjk
```

2. Create environment file:

```bash
cp .env.example .env
```

3. Start the stack:

```bash
docker-compose up --build
```

## Local URLs

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## Main API Areas

### Auth

- `POST /auth/signup`
- `POST /auth/login`
- `GET /auth/me`
- `PUT /auth/me`
- `POST /auth/logout`

### Books

- `POST /books`
- `GET /books`
- `PUT /books/{id}`
- `DELETE /books/{id}`
- `POST /books/{id}/borrow`
- `POST /books/{id}/return`
- `POST /books/{id}/reviews`
- `GET /books/{id}/analysis`
- `GET /recommendations`

## Project Structure

```text
.
|-- backend/
|   |-- app/
|   |-- tests/
|   `-- ROADMAP.md
|-- frontend/
|   `-- src/
|-- ARCHITECTURE.md
|-- DEPLOYMENT_CHECKLIST.md
|-- REQUIREMENTS_CHECKLIST.md
|-- EXECUTIVE_SUMMARY.md
|-- COMPLETION_SUMMARY.md
`-- docker-compose.yml
```

## Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
- [REQUIREMENTS_CHECKLIST.md](./REQUIREMENTS_CHECKLIST.md)
- [EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md)
- [COMPLETION_SUMMARY.md](./COMPLETION_SUMMARY.md)
- [backend/ROADMAP.md](./backend/ROADMAP.md)

## Development Notes

- Copy `.env.example` to `.env` before running locally.
- Keep provider selection configurable through environment variables.
- Prefer async-safe patterns for new backend modules.

## License

Internal project for technical assessment use.
