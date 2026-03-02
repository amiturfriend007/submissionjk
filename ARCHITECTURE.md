# LuminaLib Architecture

This document describes the current architecture and extension points.

## 1. System Overview

LuminaLib follows a layered design:

- Presentation layer: Next.js frontend
- API layer: FastAPI route handlers
- Domain/services layer: business rules and provider abstractions
- Data layer: PostgreSQL with SQLAlchemy async ORM

## 2. Data Model

Primary entities:

- `users`: identity and authentication metadata
- `books`: metadata, storage reference, generated summary
- `borrows`: borrow/return transactions
- `reviews`: ratings/comments, optional sentiment score
- `user_preferences`: key/value preferences for recommendation inputs

Design goals:

- Keep relational integrity for core entities.
- Allow recommendation features to evolve without frequent schema churn.

## 3. API and Auth

Auth is JWT-based and stateless.

- Signup/login issue and validate tokens.
- Protected endpoints resolve `current_user` through dependency injection.

Benefits:

- Horizontal scaling without sticky sessions
- Clear separation of auth concerns in dependency modules

## 4. Async and Intelligence Workloads

LLM-related operations are triggered asynchronously after request completion:

- Book summary generation on ingestion
- Review sentiment processing after submission

Current behavior is lightweight and suitable for prototype flow. For production scale, move these tasks to a dedicated worker queue.

## 5. Extensibility

### Storage

`StorageBackend` defines operations for file persistence.

- Default: local disk storage
- Planned: S3-compatible backend

### LLM

`LLMProvider` defines summarization and sentiment interfaces.

- Default: local/stub provider
- Planned: external provider integration (for example OpenAI-compatible API)

## 6. Frontend Architecture

The frontend uses Next.js App Router with TypeScript.

- SSR for core listing views
- Reusable UI components
- API service abstraction layer
- Context/hooks for auth and data flow

## 7. Deployment Topology

`docker-compose.yml` orchestrates:

1. `api` (FastAPI)
2. `frontend` (Next.js)
3. `db` (PostgreSQL)
4. `llm` (placeholder service)

Configuration is environment-driven (`.env`).

## 8. Production Hardening Priorities

- Add migrations and schema versioning
- Add queue-backed task processing
- Improve observability (metrics/logging/tracing)
- Add caching and rate limiting
- Enable TLS and reverse proxy controls

## 9. Tradeoffs

- Simpler startup path was prioritized over operational complexity.
- Abstractions are in place, but some providers remain intentionally minimal.
- Suitable for assessment/demo and structured expansion to production.
