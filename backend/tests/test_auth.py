"""
Tests for authentication endpoints.
"""
from fastapi.testclient import TestClient
from app.main import app
import pytest
import uuid

client = TestClient(app)


class TestAuthEndpoints:
    """Tests for /api/v1/auth endpoints."""
    
    def test_login_with_valid_credentials(self):
        """Test login with default admin credentials."""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_with_invalid_credentials(self):
        """Test login with wrong password."""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower() or "invalide" in response.json()["detail"].lower()
    
    def test_login_with_nonexistent_user(self):
        """Test login with non-existent user."""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "test123"}
        )
        assert response.status_code == 401
    
    def test_register_new_user(self):
        """Test registering a new user."""
        unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": unique_username,
                "email": f"{unique_username}@test.com",
                "password": "testpass123",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == unique_username
        assert data["role"] == "user"
    
    def test_register_duplicate_username(self):
        """Test registering with existing username."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "admin",
                "email": "admin2@test.com",
                "password": "testpass123",
                "full_name": "Admin 2"
            }
        )
        assert response.status_code == 400
        assert "pris" in response.json()["detail"].lower() or "exist" in response.json()["detail"].lower()
    
    def test_register_short_password(self):
        """Test registration with too short password."""
        unique_username = f"shortpass_{uuid.uuid4().hex[:8]}"
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": unique_username,
                "email": f"{unique_username}@test.com",
                "password": "short",
                "full_name": "Short Pass User"
            }
        )
        assert response.status_code == 400
    
    def test_get_current_user_without_token(self):
        """Test accessing protected endpoint without token."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    def test_get_current_user_with_token(self):
        """Test accessing protected endpoint with valid token."""
        # First login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # Then access protected endpoint
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["role"] == "admin"
    
    def test_verify_token_valid(self):
        """Test token verification with valid token."""
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        response = client.post(
            "/api/v1/auth/verify",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["valid"] == True
    
    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        response = client.post(
            "/api/v1/auth/verify",
            headers={"Authorization": "Bearer invalidtoken123"}
        )
        assert response.status_code == 401

