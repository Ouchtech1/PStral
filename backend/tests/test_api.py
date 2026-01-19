from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "ok"

def test_chat_endpoint_structure():
    # We mock the service or just test 422 for invalid payloads
    response = client.post("/api/v1/chat", json={})
    assert response.status_code == 422  # Missing messages

# Note: Full integration tests require a running Ollama instance or mocks.
# For this basic suite, we ensure the app boots and routes exist.
