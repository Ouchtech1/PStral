"""Fixtures for the deliberately small, offline demo profile."""

from __future__ import annotations

import os
from pathlib import Path
import sys
import uuid

import pytest


# Configure settings before importing the FastAPI application. The app still
# calls Ollama during startup, but a missing local daemon is an expected test
# condition and only makes /ready unavailable.
os.environ.setdefault("SECRET_KEY", "test-only-secret-key-01234567890123456789")
os.environ.setdefault("DATA_DIR", "/tmp/pstral-demo-tests")
os.environ.setdefault("OLLAMA_BASE_URL", "http://127.0.0.1:9")

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture(scope="session", autouse=True)
def clean_test_data():
    data_dir = Path(os.environ["DATA_DIR"])
    data_dir.mkdir(parents=True, exist_ok=True)
    for path in data_dir.glob("*.db*"):
        path.unlink()
    yield


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def demo_credentials():
    from app.core.auth import UserCreate, create_user

    suffix = uuid.uuid4().hex[:10]
    user = UserCreate(
        username=f"demo_{suffix}",
        email=f"demo_{suffix}@example.test",
        full_name="Demo User",
        password="demo-password-2026",
    )
    create_user(user)
    return user.username, user.password


@pytest.fixture
def auth_headers(client, demo_credentials):
    username, password = demo_credentials
    response = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
