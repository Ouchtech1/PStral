"""
Pytest configuration and fixtures for Pstral tests.
"""
import pytest
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize databases before tests
from app.core.auth import init_users_db
from app.infrastructure.database.feedback_db import init_db as init_feedback_db
from app.infrastructure.database.audit_db import init_audit_db
from app.infrastructure.database.conversations_db import init_conversations_db


@pytest.fixture(scope="session", autouse=True)
def setup_databases():
    """Initialize all databases before running tests."""
    init_users_db()
    init_feedback_db()
    init_audit_db()
    init_conversations_db()
    yield


@pytest.fixture
def auth_headers():
    """Get authentication headers for tests."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

