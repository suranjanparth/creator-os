# CREATOR OS

CREATOR OS is an AI-powered Creator Intelligence, Strategy, and Content Operating System. This repository contains the full product: a Next.js dashboard shell, a FastAPI API, PostgreSQL infrastructure, and Docker-based local development.

## Architecture

- `apps/web`: Next.js and TypeScript frontend.
- `apps/api`: FastAPI backend, SQLAlchemy database infrastructure, and Alembic migrations.
- PostgreSQL is the source of truth for creator data and evidence-backed insights.
- The browser communicates with FastAPI through `NEXT_PUBLIC_API_BASE_URL`. Server-only secrets remain in the API environment.

Dashboard metrics, Content Intelligence, Creator DNA, Analytics, and Recommendations are all derived deterministically from persisted creator content. Every response carries a `data_source` of `"development"` (derived from seeded persisted rows) or `"empty"` (no data yet); the UI shows an honest empty state rather than fabricated numbers.

## Database Setup

Content Intelligence analyzes persisted creator content.

**Local development (no setup required):** when `DATABASE_URL` is not set in `apps/api/.env`, the API automatically runs against a file-backed SQLite database at `apps/api/creator_os_local.db`. On startup it creates the persistence tables and seeds the documented development dataset (Maya's six posts). Nothing else is required to run locally.

**PostgreSQL:** set `DATABASE_URL` in `apps/api/.env` to your PostgreSQL connection, then apply migrations and seed the development dataset:

```bash
cd apps/api
DATABASE_URL="postgresql+psycopg://creator_os:replace-with-a-local-development-password@localhost:5432/creator_os" .venv/bin/alembic upgrade head
.venv/bin/python -m app.seed
```

PostgreSQL remains the source of truth for any environment other than local development. The seed is idempotent: it loads Maya's six development posts into `creator_content` only when they are not already present.

## Prerequisites

- Node.js 22 or newer.
- Python 3.11 or newer.
- Docker Desktop for the containerized setup, or a local PostgreSQL 17-compatible instance.

## Environment

Copy the examples before running locally:

```bash
cp .env.example .env
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
```

Set `DATABASE_URL` in `apps/api/.env` to your local PostgreSQL connection. The root `.env` is used by Docker Compose. Do not commit either file.

## Install Dependencies

Frontend:

```bash
npm install
```

Backend:

```bash
python3 -m venv apps/api/.venv
apps/api/.venv/bin/pip install -r apps/api/requirements.txt
```

## Run Locally

With Docker:

```bash
docker compose up --build
```

Without Docker, the API uses the file-backed SQLite database automatically. Run these in separate terminals:

```bash
npm run dev:web
```

```bash
apps/api/.venv/bin/uvicorn app.main:app --app-dir apps/api --reload --port 8000
```

For PostgreSQL instead of SQLite, start PostgreSQL first and set `DATABASE_URL` in `apps/api/.env`.

Open `http://localhost:3000`. The frontend health card requests `http://localhost:8000/api/v1/health` by default.

## Tests and Checks

```bash
npm run typecheck:web
npm run test:web
npm run build:web
apps/api/.venv/bin/pytest apps/api/tests
```

The API health endpoint is available at `GET /api/v1/health`.

## API Endpoints

All endpoints are served under `/api/v1` and accept an optional `creator_id` query parameter (defaulting to the seeded development creator `maya-chen`).

- `GET /api/v1/health` — API process status.
- `GET /api/v1/dashboard` — creator dashboard metrics, trend, content, and a deterministic format insight.
- `GET /api/v1/analytics` — totals, platform breakdown, top posts, trend, and engagement anatomy derived from persisted content.
- `GET /api/v1/content-intelligence` — deterministic per-post performance analysis.
- `GET /api/v1/creator-dna` — format/platform shares, best format, engagement benchmark, and creative insights.
- `GET /api/v1/recommendations` — evidence-linked next-move recommendations.
- `GET /api/v1/creators/{creator_id}` — a persisted creator profile (404 when missing).
- `GET /api/v1/creators` — persisted creator profiles, ordered by name, for active creator selection.
- `POST /api/v1/creators` — create or update a creator profile (JSON body).
- `POST /api/v1/content` — ingest a single creator content record (JSON body).
- `POST /api/v1/content/ingest` — batch ingest. Every item is written under the request's `creator_id`; duplicate ids are skipped.
- `POST /api/v1/ingestion/import` — creator-scoped import of a normalized creator payload (profile + published content). The profile is upserted; each content item is created, updated, or skipped idempotently, and per-item validation failures are reported in the response without failing the whole sync.
- `GET /api/v1/content` — creator-scoped content retrieval (`?creator_id=`).

## Ingestion & Provider Boundary

The ingestion pipeline lives in `apps/api/app/domains/ingestion` and consumes **normalized** creator payloads:

```json
{
  "creator_id": "maya-chen",
  "profile": { "name": "Maya Chen", "handle": "@mayamakes", "platform": "Instagram", "follower_count": 84200 },
  "content": [
    { "id": "post-1", "platform": "Instagram", "content_type": "Reel", "category": "Creative systems", "title": "A reel", "views": 12000 }
  ]
}
```

The response reports `profile_status` (`created`/`updated`/`unchanged`), `content_received`, `created`, `updated`, `skipped`, `errors`, and a per-item outcome list. Re-importing the same payload is idempotent.

External platforms plug in through `apps/api/app/domains/ingestion/providers`: a `ProviderClient` boundary returns normalized `ProviderCreator` / `ProviderPost` data that the pipeline persists. The included `InstagramProvider` is an honest integration seam — it never fabricates platform data and raises `ProviderNotConfigured` until credentials are present.

### Instagram/Meta credentials required later

A real Instagram integration needs a Meta App (Instagram Graph API / Instagram Login with Advanced Access) and these **server-side** environment variables in the API environment:

- `INSTAGRAM_APP_ID` and `INSTAGRAM_APP_SECRET` — Meta app credentials.
- `INSTAGRAM_REDIRECT_URI` — the OAuth callback URL.
- `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_USER_ID` — obtained after the authorized user completes OAuth.

Required Graph API permission: `instagram_business_basic` (read the authorized user's published media and public engagement counts). OAuth approval depends on Meta's app review; until then the development import path (the Connect page / `POST /api/v1/ingestion/import`) exercises the same real pipeline with explicitly provided data.
