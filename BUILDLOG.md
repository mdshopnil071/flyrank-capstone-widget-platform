# Build log

- AI helped audit the original implementation against the capstone brief and identify missing CRUD, validation limits, idempotency, background work, deterministic provider controls, analytics, and documentation.
- The initial evidence claimed CRUD and snippet generation, but the code had no update endpoint or snippet generator. Those claims were corrected by adding `PATCH /api/widgets/{id}` and `GET /api/widgets/{id}/snippet`.
- The initial public widget rendered server-provided strings through `innerHTML` without escaping. The bundle now escapes title, description, and button text before interpolation.
- Notification work moved to FastAPI `BackgroundTasks`; the response commits the submission before scheduling the non-critical side effect.
- This is a local capstone implementation: the in-memory rate limiter and console notification are documented limitations.
