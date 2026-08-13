# Repository Notes

- This is a two-application repository: `apps/web` is the Next.js/TypeScript frontend and `apps/api` is the FastAPI/Python backend. Keep frontend and backend concerns separate.
- PostgreSQL is the source of truth. Add database changes through SQLAlchemy models and Alembic migrations; do not create schema changes outside migrations.
- The backend is a modular monolith. Place domain behavior in `apps/api/app/domains/<domain>` and keep API route handlers thin.
- AI output must use versioned prompts and validated structured schemas. Do not add fake AI output, synthetic analytics, or unsupported creator-specific claims.
- Creator-specific DNA and recommendations must retain evidence links, sample size, and confidence once implemented; use general guidance when evidence is insufficient.
- Do not add Redis, background workers, S3, platform integrations, microservices, or a dedicated vector database without a concrete approved requirement.
- Store local development media through `apps/api/app/storage` so storage can later move to S3-compatible infrastructure without changing domain logic.
- Use server-side environment variables for database and AI credentials. Only variables prefixed `NEXT_PUBLIC_` may be exposed to the browser, and they must never contain secrets.
- Before submitting changes, run `npm run typecheck:web`, `npm run test:web`, and `apps/api/.venv/bin/pytest apps/api/tests` when dependencies are available.
