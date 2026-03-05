# LuminaLib Frontend

Frontend application for LuminaLib, built with Next.js App Router, React, TypeScript, React Query, and Tailwind CSS.

## What This App Provides

- Server-rendered home page with live book listing
- Book upload flow (`.txt` and `.pdf`)
- Borrow/return and review actions from the UI
- Rolling sentiment/consensus visibility per book
- Authentication pages (signup, login, profile)
- LLM status and chat screen
- Download/view actions for uploaded book files

## Tech Stack

- Next.js 14
- React 18
- TypeScript
- Axios
- @tanstack/react-query
- Tailwind CSS
- Jest + React Testing Library

## Directory Structure

```text
frontend/
|-- src/
|   |-- app/
|   |   |-- auth/
|   |   |-- books/new/
|   |   |-- llm/
|   |   |-- error.tsx
|   |   |-- globals.css
|   |   |-- layout.tsx
|   |   `-- page.tsx
|   |-- components/
|   |   |-- BookCard.tsx
|   |   |-- PendingSummaryRefresher.tsx
|   |   |-- RecommendedBooks.tsx
|   |   `-- __tests__/
|   |-- context/
|   |   `-- AuthContext.tsx
|   |-- hooks/
|   |   |-- useBooks.ts
|   |   `-- __tests__/
|   `-- services/
|       |-- api.ts
|       `-- books.ts
|-- Dockerfile
|-- jest.config.js
|-- jest.setup.ts
|-- package.json
|-- postcss.config.js
|-- tailwind.config.js
`-- tsconfig.json
```

## Prerequisites

- Node.js 18+
- npm 9+
- Running backend API (default: `http://localhost:8000`)

## Local Development

1. Go to frontend folder:

```bash
cd c:\Amit\submissionjk\frontend
```

2. Install dependencies:

```bash
npm install
```

3. Configure environment:

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start dev server:

```bash
npm run dev
```

5. Open app:

- `http://localhost:3000`

## Available Scripts

- `npm run dev` - start development server
- `npm run build` - production build
- `npm run start` - run production build
- `npm run lint` - run Next.js lint
- `npm run test` - run Jest tests

## API Integration

All API calls are centralized through `src/services/api.ts` and `src/services/books.ts`.

### Base URL

- Reads `NEXT_PUBLIC_API_URL`
- Falls back to `http://localhost:8000`

### Auth Header Behavior

- Request interceptor adds `Authorization: Bearer <token>` if token exists in `localStorage`
- Response interceptor clears local token on `401`

### Backend Routes Used

- Auth: `/auth/signup`, `/auth/login`, `/auth/me`
- Books: `/books/`, `/books/{id}/borrow`, `/books/{id}/return`, `/books/{id}/reviews`, `/books/{id}/analysis`, `/books/{id}/download`, `/books/{id}/view`, `/books/{id}/summary/refresh`, `/books/recommendations`
- LLM: `/llm/status`, `/llm/chat`

## App Routes

- `/` - home page, SSR books list + recommendations
- `/books/new` - upload a book
- `/auth/login` - login form
- `/auth/signup` - signup form
- `/auth/profile` - profile view/update + logout
- `/llm` - LLM status and chat UI

## State Management

- `AuthContext` holds auth token and login/logout actions
- React Query powers data fetching/caching (`useBooks`)
- Book actions trigger refreshes for up-to-date server state

## Styling

- Tailwind + custom CSS variables in `src/app/globals.css`
- Shared UI primitives: `.panel`, `.btn`, `.input-field`, `.page-shell`
- Responsive layout with clean light theme and gradient background

## Testing

Run tests:

```bash
npm test
```

Current test areas:

- `src/components/__tests__/BookCard.test.tsx`
- `src/hooks/__tests__/useBooks.test.ts`

## Docker

Build and run frontend container only:

```bash
cd c:\Amit\submissionjk\frontend
docker build -t luminalib-frontend .
docker run --rm -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://host.docker.internal:8000 luminalib-frontend
```

For full-stack local setup, use project root `docker-compose.yml`.

## Troubleshooting

### Frontend cannot reach API

- Verify backend is running
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`
- Check browser network tab for failing endpoints

### Login succeeds but protected actions fail

- Confirm token is present in `localStorage` (`token` key)
- Re-login if token expired or invalidated

### Upload fails

- Ensure file is `.txt` or `.pdf`
- Check backend response in network panel for validation details

### LLM page shows disconnected

- Confirm backend `/llm/status` works
- Confirm backend LLM provider URL/model are configured and reachable

## Notes

- `tsconfig.json` currently has `strict: false`.
- `next.config.js` is not present; defaults are currently used.
- Error UI fallback is implemented at `src/app/error.tsx`.
