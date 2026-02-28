# LuminaLib

A next-generation intelligent library system built with FastAPI (Python) and
Next.js (React).  It supports file upload, JWT auth, asynchronous LLM
summarization, review sentiment analysis, and a pluggable storage/LLM
architecture.

## Features

- **JWT-based Authentication**: Stateless, secure token management
- **Book Management**: Upload and manage book files with metadata
- **Smart Reviews**: Submit and track review sentiment using LLM
- **Recommendation Engine**: ML-driven book suggestions based on user preferences
- **Async Processing**: Background tasks for LLM summarization and sentiment analysis
- **Abstracted Providers**: Swap storage (local ↔ S3) and LLM backends easily
- **SSR Frontend**: Next.js with server-side rendering for performance
- **Docker-Ready**: One-command deployment with `docker-compose`

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- (Optional) `.env` file for custom configuration

### Installation & Running

1. Clone the repository:

```bash
cd c:\Amit\submissionjk
```

2. Create `.env` from template:

```bash
cp .env.example .env
```

You can customize JWT_SECRET and other settings if desired.

3. Start all services:

```bash
docker-compose up --build
```

This command will:

- Build the FastAPI backend
- Build the Next.js frontend
- Start PostgreSQL 15
- Initialize the database
- Serve the API on `http://localhost:8000`
- Serve the frontend on `http://localhost:3000`
- Provide interactive API docs at `http://localhost:8000/docs`

## API Documentation

### Core Endpoints

**Authentication**
- `POST /auth/signup` – Register new user
- `POST /auth/login` – Get JWT token
- `GET /auth/me` – Read current user profile
- `PUT /auth/me` – Update profile
- `POST /auth/logout` – Logout (client discards token)

**Books**
- `POST /books` – Upload book file (triggers async summary)
- `GET /books?page=1` – List all books with pagination
- `PUT /books/{id}` – Update book metadata
- `DELETE /books/{id}` – Remove book and file
- `POST /books/{id}/borrow` – Borrow a book
- `POST /books/{id}/return` – Return a borrowed book
- `POST /books/{id}/reviews` – Create review (only if borrowed)
- `GET /books/{id}/analysis` – Get aggregated review sentiment
- `GET /recommendations` – Get personalized book suggestions

### Example Requests

See [API_EXAMPLES.rest](./API_EXAMPLES.rest) for detailed request examples.

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed design decisions, including:

- Database schema rationale
- Asynchronous task handling
- Recommendation strategy
- Frontend design and component composition
- Swappability of storage and LLM providers

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app
│   │   ├── core/                   # Config, security, JWT
│   │   ├── db/                     # Database models, session
│   │   ├── api/routes/             # Route handlers
│   │   ├── schemas/                # Pydantic models
│   │   ├── services/               # Storage, LLM, recommendations
│   │   └── tasks/                  # Background jobs
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/                      # Unit tests
├── frontend/
│   ├── src/
│   │   ├── app/                    # Next.js pages
│   │   ├── components/             # Reusable React components
│   │   ├── hooks/                  # Custom React hooks
│   │   ├── services/               # HTTP client abstraction
│   │   ├── context/                # React Context (Auth)
│   │   └── components/__tests__/   # Component unit tests
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── jest.config.js
│   ├── Dockerfile
│   └── next.config.js
├── docker-compose.yml              # Complete stack orchestration
├── ARCHITECTURE.md                 # Design documentation
├── README.md                       # This file
└── .env.example                    # Template for environment variables
```

## Environment Variables

Copy `.env.example` to `.env` and modify as needed:

```ini
# Database (postgres container will use these)
DATABASE_URL=postgresql+asyncpg://lumina:lumina@db:5432/luminalib

# JWT
JWT_SECRET=change-me

# Storage
STORAGE_BACKEND=local              # or "s3" with appropriate AWS config
STORAGE_PATH=./data

# LLM
LLM_PROVIDER=local                 # or "openai" etc.
LLM_URL=http://localhost:8001
```

## Testing

### Backend

```bash
cd backend
pytest
```

### Frontend

```bash
cd frontend
npm test
```

## Development

### Backend

For local development without Docker:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server will run on `http://localhost:3000`.

## Production Considerations

- Set `JWT_SECRET` to a strong random value
- Use a managed PostgreSQL service
- Integrate with a real LLM provider (OpenAI, Hugging Face, etc.)
- Switch storage backend to AWS S3 or similar
- Use a real task queue (Celery, RQ) for background jobs
- Enable CORS appropriately
- Set up logging and monitoring

## Related Documentation

- [Backend Architecture](./ARCHITECTURE.md)
- [API Examples](./API_EXAMPLES.rest)

---

**LuminaLib** © 2026. A production-grade library system with AI-powered features.
