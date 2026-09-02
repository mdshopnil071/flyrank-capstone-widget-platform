# FlyRank Embeddable Widget Platform

A small FastAPI service for creating tenant-isolated signup, CTA, and popover widgets. A customer installs a widget with one script tag; visitors submit validated data from another origin; the service rate-limits and honeypot-checks requests, enriches IP data with a fallback chain, stores submissions, and sends notifications in a background task.

## Architecture

```text
Owner + JWT -> Widget API -> Supabase PostgreSQL
Customer site -> cached widget config + versioned JS
Visitor -> CORS submission -> validation -> abuse checks -> geo fallback -> database
                                      `-> background notification (failure isolated)
Owner + JWT -> Dashboard submissions, totals, geo and per-widget stats
```

## Run locally

1. Copy `.env.example` to `.env`, set your Supabase `DATABASE_URL`, and set a strong `JWT_SECRET`. The app connects to Supabase PostgreSQL over SSL.
2. Install dependencies: `python -m pip install -r requirements.txt`.
3. Start the API: `uvicorn app.main:app --reload`.
4. Seed demo data: `python -m app.seed`.
5. Serve `test_origin` separately: `python -m http.server 5500 --directory test_origin`.

Docker users can run `docker compose up --build` after creating `.env`; Compose uses the Supabase database configured there and does not start a local database.

Demo login: `demo@example.com` / `demo-password-123`. Passwords are stored with PBKDF2-SHA256.

## API highlights

- `POST /api/auth/register`, `POST /api/auth/login`
- Authenticated widget CRUD: `/api/widgets`
- `GET /api/widgets/{id}/snippet` returns the paste-ready script tag
- Public cached config: `GET /api/public/widgets/{id}/config`
- Public CORS submission: `POST /api/public/widgets/{id}/submit`
- Send `Idempotency-Key` to make retries create one submission
- Authenticated dashboard: `/api/dashboard/submissions`, `/api/dashboard/stats`, `/api/dashboard/widgets/{id}/stats`
- `OPTIONS` requests are handled by FastAPI CORS middleware

## Verification controls

Set `MOCK_GEO_PROVIDER_A=true` or `MOCK_GEO_PROVIDER_B=true` for deterministic geo responses. Toggle `GEO_PROVIDER_A_ENABLED` and `GEO_PROVIDER_B_ENABLED` to prove provider fallback and all-provider degradation. Set `NOTIFICATION_FAIL=true` to prove notification failure does not affect the stored submission.

## Database migrations

The repository includes Alembic migrations. Run `alembic upgrade head` against the Supabase database before deployment. The application also keeps `create_all` for a frictionless first local run.

## Limitations

The notification is a local console side effect and rate limiting uses in-memory storage. The test page uses a manually copied snippet from the authenticated API.
