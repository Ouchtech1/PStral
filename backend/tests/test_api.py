from __future__ import annotations


def test_health_is_public_and_docs_are_disabled(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404


def test_chat_requires_authentication(client):
    response = client.post(
        "/api/v1/chat",
        json={"mode": "chat", "messages": [{"role": "user", "content": "Bonjour"}]},
    )
    assert response.status_code == 401


def test_chat_payload_is_bounded(client, auth_headers):
    response = client.post(
        "/api/v1/chat",
        headers=auth_headers,
        json={"mode": "chat", "messages": [{"role": "user", "content": "x" * 2001}]},
    )
    assert response.status_code == 422


def test_removed_demo_features_have_no_route(client, auth_headers):
    assert client.post("/api/v1/sql/execute", headers=auth_headers, json={"query": "SELECT 1"}).status_code == 404
    assert client.get("/api/v1/conversations/", headers=auth_headers).status_code == 404
    assert client.post("/api/v1/feedback/", headers=auth_headers, json={}).status_code == 404
