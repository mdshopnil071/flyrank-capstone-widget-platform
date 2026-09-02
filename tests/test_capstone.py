import os

os.environ["DATABASE_URL"] = "sqlite:///./test_widget_platform.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["MOCK_GEO_PROVIDER_A"] = "true"

from fastapi.testclient import TestClient
from app.database import Base, engine
from app.main import app

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
client = TestClient(app)


def auth_headers():
    client.post("/api/auth/register", json={"email": "owner@example.com", "password": "password-123"})
    token = client.post("/api/auth/login", data={"username": "owner@example.com", "password": "password-123"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_widget_crud_snippet_and_idempotency():
    headers = auth_headers()
    created = client.post("/api/widgets", headers=headers, json={"title": "Newsletter"})
    assert created.status_code == 201
    widget_id = created.json()["id"]
    assert client.patch(f"/api/widgets/{widget_id}", headers=headers, json={"button_text": "Join"}).status_code == 200
    snippet = client.get(f"/api/widgets/{widget_id}/snippet", headers=headers)
    assert "widget.v1.js" in snippet.json()["snippet"]
    payload = {"name": "Ada", "email": "ada@example.com"}
    first = client.post(f"/api/public/widgets/{widget_id}/submit", json=payload, headers={"Idempotency-Key": "demo-1"})
    second = client.post(f"/api/public/widgets/{widget_id}/submit", json=payload, headers={"Idempotency-Key": "demo-1"})
    assert first.status_code == 201 and second.json()["deduplicated"] is True


def test_validation_cors_and_oversized_request():
    headers = auth_headers()
    widget_id = client.post("/api/widgets", headers=headers, json={"title": "Contact"}).json()["id"]
    invalid = client.post(f"/api/public/widgets/{widget_id}/submit", json={"name": ""})
    assert invalid.status_code == 422
    preflight = client.options(f"/api/public/widgets/{widget_id}/submit", headers={"Origin": "http://localhost:5500", "Access-Control-Request-Method": "POST"})
    assert preflight.status_code == 200
    oversized = client.post(f"/api/public/widgets/{widget_id}/submit", headers={"Content-Length": "20000"}, content="{}")
    assert oversized.status_code == 413
