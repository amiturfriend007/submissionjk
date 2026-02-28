# LuminaLib Architecture

This document explains high-level architectural choices for the LuminaLib
intelligent library system.

## 1. Database Schema

The schema uses a single relational PostgreSQL database with the following
tables:

* **users** – holds authentication information (email, hashed_password, etc.).
* **books** – each record references a stored file path and holds metadata and
  LLM-generated summary.
* **borrows** – junction table capturing which user has borrowed which book and
  when they returned it.
* **reviews** – user ratings/comments along with an LLM `sentiment_score`.
* **user_preferences** – simple key/value store used by the recommendation
  engine.  This design allows arbitrary preferences (genres, authors,
etc.) without altering the schema.  The rationale was to avoid a complex
  many‑to‑many relationship and keep the recommendation logic focused on
  whatever dimensions our algorithm finds useful.

Rolling consensus (average rating) is stored on-demand when reviews arrive.  We
could push that into its own table for large scale, but the prototype updates the
`book.description` for simplicity.

## 2. Asynchronous LLM Processing

FastAPI's `BackgroundTasks` drive asynchronous work.  The API simply registers
internal coroutine tasks after the request completes, keeping the HTTP layer
light and stateless.  The tasks run in the same event loop; swapping to a queue
(e.g. Celery/RabbitMQ) would be a one‑line change in the task module.  The
storage/LLM/rec modules expose simple interfaces so production can replace
autonomous services.

*Book ingestion* reads the uploaded file synchronously then dispatches
`generate_summary` in the background.  For real content we’d offload heavy
parsing to a worker and possibly store intermediary data in an object store.

*Review analysis* is similar: when a review is created, background tasks trigger
sentiment analysis and a consensus update.

## 3. Recommendation Strategy

The `user_preferences` table stores arbitrary key/value pairs—think of them as
feature vectors.  The prototype recommendation endpoint simply returns an empty
list, but the schema enables both content‑based (matching book metadata to the
user's saved preferences) and collaborative filtering (aggregating preferences
over similar users).  Implementing the actual algorithm would involve a
scheduled job reading these tables, computing similarity, and caching results or
calling them in real time.

## 4. Frontend Design Choices

The frontend uses Next.js (app router) to enable SSR on critical pages.  Pages
are composed of small, testable components; for example, a `BookCard`,
`ReviewForm`, and `BorrowButton` live in `src/app/components` (not yet added in
this initial scaffold).  Network calls are abstracted through a `services/api.ts`
module and wrapped in React Query hooks to manage caching and loading states.  We
avoid direct `fetch` in components.

Styling is handled with Tailwind CSS configured via the `tailwind.config.js`
file (not yet added).  This keeps styles utility‑first and responsive without
sacrificing consistency.

## 5. Swappability & Extensibility

* **Storage**: The `StorageBackend` interface sits in `services/storage.py`. The
  default `LocalStorage` writes to disk; swapping to AWS S3 only requires
  implementing the same interface and setting `STORAGE_BACKEND=s3` in the
  environment.
* **LLM**: A provider interface in `services/llm.py` allows substituting a local
  stub with an external API (OpenAI, LLM Node) by implementing `summarize`
and `analyze_sentiment`.  The provider is selected by the `LLM_PROVIDER`
config value.
* **Database**: Using SQLAlchemy's async engine with `Base.metadata.create_all`
  on startup makes it easy to point at a new Postgres instance or a different
  database entirely.

## 6. Docker & Environment

A `docker-compose.yml` orchestrates four containers:

1. **api** – the FastAPI service exposing `/auth`, `/books`, etc.
2. **frontend** – the Next.js application.
3. **db** – PostgreSQL 15 with volume persistence.
4. **llm** – a placeholder container; in production this would run a llama 3
   compatible service or proxy to an external LLM.

Env vars are managed via `.env` files and passed through compose in the
`environment` section.  The one‑command start is `docker-compose up --build`.

---

This architecture balances production‑grade patterns with the simplicity needed
for an initial proof‑of‑concept.  Clean separation and DI make later extensions
(such as full ML jobs or a cloud storage migration) straightforward.