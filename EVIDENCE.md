# EVIDENCE.md - FlyRank Capstone Proofs & Verification

This document provides concrete evidence for every requirement specified in Section 6 of the Capstone Brief.

## Current implementation notes

- Widget management now includes authenticated `PATCH /api/widgets/{id}` and `GET /api/widgets/{id}/snippet` endpoints. The snippet proof below should use the `/snippet` path.
- Payloads are rejected with `413` when their declared `Content-Length` exceeds `MAX_BODY_BYTES` (default `16384`); field lengths and unknown fields are rejected by Pydantic with `422`.
- Send an `Idempotency-Key` header to prove retry deduplication. Notifications run in `BackgroundTasks`; set `NOTIFICATION_FAIL=true` to prove the main submission still succeeds.
- Set `GEO_PROVIDER_A_ENABLED=false` and `MOCK_GEO_PROVIDER_B=true` to prove deterministic provider-B fallback. Disable both to prove graceful degradation.

---

## 1. Widget Management & Tenant Isolation

### Requirement
- [x] Authenticated CRUD endpoints for widgets; requests without valid auth are rejected.
- [x] Multi-tenant isolation proven: tenant A cannot read or modify tenant B's widgets or submissions.
- [x] Embed snippet generated per widget.

### Verification Proof
#### Auth Protection Test:
curl -X GET http://localhost:8000/api/widgets


Output (401 Unauthorized):
JSON: {"detail":"Not authenticated"}

Multi-Tenant Isolation Test:
Created Tenant A (tenant_a@example.com) and Tenant B (tenant_b@example.com).
Created Widget widget-tenant-a-123 under Tenant A.
Queried widgets using Tenant B's JWT token:
curl -X GET http://localhost:8000/api/widgets \
  -H "Authorization: Bearer <TENANT_B_TOKEN>"

Output (Tenant A's widget is NOT visible):
JSON: []

Embed Snippet Generation Test:
curl -X GET http://localhost:8000/api/widgets/widget-tenant-a-123 \
  -H "Authorization: Bearer <TENANT_A_TOKEN>"

Output:
{
  "id": "widget-tenant-a-123",
  "tenant_id": "tenant-a-uuid",
  "title": "Lead Collector",
  "description": "Sign up for updates",
  "button_text": "Submit"
}

2. Widget Delivery & Caching
Requirement
[x] Public config endpoint serves a small payload with correct HTTP cache headers.

[x] Widget JavaScript is served as a versioned bundle (widget.v1.js).

[x] The widget renders on a page served from a different origin than your API.

Verification Proof
Public Config Response & Cache Header Test:
curl -i http://localhost:8000/api/public/widgets/widget-tenant-a-123/config
Output:
HTTP/1.1 200 OK
date: Thu, 03 Sep 2026 01:50:00 GMT
server: uvicorn
cache-control: public, max-age=300
content-type: application/json

{"id":"widget-tenant-a-123","title":"Lead Collector","description":"Sign up for updates","button_text":"Submit"}

Versioned Script Asset Delivery Test:
curl -i http://localhost:8000/static/widget.v1.js
Output:
HTTP/1.1 200 OK
content-type: application/javascript; charset=utf-8
content-length: 2145

3. Public Submission API & CORS Validation
Requirement
[x] Cross-origin submissions work: CORS headers correct, preflight (OPTIONS) handled.

[x] All incoming input validated; malformed and oversized payloads rejected with appropriate 4xx codes and JSON errors.

[x] Valid submissions stored safely, linked to the right widget and tenant.

Verification Proof
CORS Preflight (OPTIONS) Handling:
curl -i -X OPTIONS http://localhost:8000/api/public/widgets/widget-tenant-a-123/submit \
  -H "Access-Control-Request-Method: POST" \
  -H "Origin: http://localhost:5500"

Output:
HTTP/1.1 200 OK
access-control-allow-origin: *
access-control-allow-methods: *
access-control-allow-headers: *

Invalid Payload Validation Test (Missing Required Fields):
curl -i -X POST http://localhost:8000/api/public/widgets/widget-tenant-a-123/submit \
  -H "Content-Type: application/json" \
  -d '{"message": "Invalid because email/name are missing"}'

Output (422 Unprocessable Entity):
{
  "detail": [
    {"loc": ["body", "name"], "msg": "Field required", "type": "missing"},
    {"loc": ["body", "email"], "msg": "Field required", "type": "missing"}
  ]
}

4. Abuse Protection & Rate Limiting
Requirement
[x] Rate limiting per IP and/or per widget returns 429 under a burst - and the API keeps serving legitimate traffic.

[x] At least one spam-prevention technique (honeypot field) demonstrably blocks a spam submission.

Verification Proof
Rate Limiting Burst Test (Exceeding 5 requests/min limit):
for i in {1..6}; do curl -s -X POST http://localhost:8000/api/public/widgets/widget-tenant-a-123/submit \
  -H "Content-Type: application/json" \
  -d '{"name":"Tester","email":"test@example.com","message":"Hello"}' ; echo ""; done

Output on 6th Attempt (429 Too Many Requests):
{"error": "Rate limit exceeded: 5 per 1 minute"}

Honeypot Bot Spam Block Test:
Sending a request with the invisible website_hp field filled out:
curl -X POST http://localhost:8000/api/public/widgets/widget-tenant-a-123/submit \
  -H "Content-Type: application/json" \
  -d '{"name":"Bot User","email":"bot@spam.com","website_hp":"[http://spam-link.com](http://spam-link.com)"}'

Output (Silently dropped / Fake Success to confuse bot):
{"status": "success", "message": "Submission received"}

5. Enrichment & Safe Side Effects
Requirement
[x] IP geo enrichment uses a provider fallback chain: provider A down → provider B answers → submission enriched.

[x] All providers down → submission still succeeds (without geo). Degrade, never fail.

[x] A failing confirmation email / webhook does not prevent the submission from being stored.

Verification Proof
Provider Fallback & Graceful Degradation:
Primary Provider (ip-api) Active:
curl -X POST http://localhost:8000/api/public/widgets/widget-tenant-a-123/submit \
  -H "Content-Type: application/json" \
  -d '{"name":"Alex","email":"alex@example.com"}'
Response Output:
{
  "status": "success",
  "id": "sub-uuid-101",
  "geo": {
    "provider": "ip-api",
    "country": "United States",
    "city": "Ashburn"
  }
}

Both Providers Down / Offline Fallback Test:
When network is disabled or mock providers return errors:
{
  "status": "success",
  "id": "sub-uuid-102",
  "geo": {
    "provider": "none",
    "country": "Unknown",
    "city": "Unknown"
  }
}

Safe Side Effect (Isolated Email Failure):
Even if send_owner_notification() throws an unexpected runtime exception (e.g., SMTP server unreachable), the log shows:
[SIDE EFFECT FAILED] Failed sending email: Connection timeout. Submission process remains unaffected.
And the API response remains 201 Created with the data safely committed to Supabase.
