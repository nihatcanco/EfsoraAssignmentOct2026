# BriefBase

A small notes app. You paste some text, and the backend generates a short summary and 3-5 tags for it. You can
filter notes by tag, re-summarize them and delete them. Each user only sees their own notes.

## Tech choices

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2, Alembic for migrations
- **Database:** PostgreSQL 17 (Neon in production)
- **Auth:** email + password (bcrypt), JWT Bearer token
- **Frontend:** Next.js 16 (App Router, TypeScript), TanStack React Query
- **Hosting:** Vercel (frontend), Render (backend), Neon (Postgres)

## Running locally

Copy the env file and fill in the values:

| Variable              | Description                                                         |
| --------------------- | ------------------------------------------------------------------- |
| `DATABASE_URL`        | Postgres URL. docker compose points it at the `db` container.       |
| `JWT_SECRET`          | Secret for signing tokens. Generate one with `openssl rand -hex 32`. |
| `JWT_EXPIRE_MINUTES`  | Token lifetime, default 1440 (24h).                                 |
| `ANTHROPIC_API_KEY`   | Anthropic API key. Without it, notes are saved without summaries.   |
| `ANTHROPIC_MODEL`     | Default `claude-opus-5-5`.                                          |
| `CORS_ORIGINS`        | Comma separated frontend origins, default `http://localhost:3000`.  |
| `NEXT_PUBLIC_API_URL` | Backend URL for the frontend, default `http://localhost:8000`.      |

Start everything:

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- API: http://localhost:8000 (docs at http://localhost:8000/docs)

Migrations run automatically when the backend container starts. To run them by hand:

```bash
docker compose exec backend alembic upgrade head
```

## Live app

- **Frontend (Vercel):** https://efsora-assignment-oct2026.vercel.app
- **Backend:** Hosted on Render. It's on the free tier, so the first request after it has been idle can take 50+ seconds.

## Test account

You can register a new account from the login page with any email and password.

## AI provider

Anthropic Claude (`claude-opus-5-5`) through the official Python SDK.
