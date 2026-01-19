"""
Tests for conversations database and endpoints.
"""
from fastapi.testclient import TestClient
from app.main import app
import pytest
import uuid

client = TestClient(app)


def get_auth_headers():
    """Helper to get authentication headers."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestConversationsEndpoints:
    """Tests for /api/v1/conversations endpoints."""
    
    def test_list_conversations_requires_auth(self):
        """Test that listing conversations requires authentication."""
        response = client.get("/api/v1/conversations/")
        assert response.status_code == 401
    
    def test_list_conversations_authenticated(self):
        """Test listing conversations when authenticated."""
        response = client.get(
            "/api/v1/conversations/",
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        assert "conversations" in response.json()
        assert isinstance(response.json()["conversations"], list)
    
    def test_create_conversation(self):
        """Test creating a new conversation."""
        conv_id = str(uuid.uuid4())
        response = client.post(
            "/api/v1/conversations/",
            headers=get_auth_headers(),
            json={
                "id": conv_id,
                "mode": "sql",
                "title": "Test Conversation"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == conv_id
        assert data["mode"] == "sql"
        assert data["title"] == "Test Conversation"
    
    def test_get_conversation(self):
        """Test getting a specific conversation."""
        # First create one
        conv_id = str(uuid.uuid4())
        client.post(
            "/api/v1/conversations/",
            headers=get_auth_headers(),
            json={"id": conv_id, "mode": "chat", "title": "Get Test"}
        )
        
        # Then retrieve it
        response = client.get(
            f"/api/v1/conversations/{conv_id}",
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        assert response.json()["id"] == conv_id
    
    def test_get_nonexistent_conversation(self):
        """Test getting a conversation that doesn't exist."""
        response = client.get(
            "/api/v1/conversations/nonexistent-id",
            headers=get_auth_headers()
        )
        assert response.status_code == 404
    
    def test_update_conversation(self):
        """Test updating a conversation."""
        # Create
        conv_id = str(uuid.uuid4())
        client.post(
            "/api/v1/conversations/",
            headers=get_auth_headers(),
            json={"id": conv_id, "mode": "sql", "title": "Original Title"}
        )
        
        # Update
        response = client.put(
            f"/api/v1/conversations/{conv_id}",
            headers=get_auth_headers(),
            json={
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there!"}
                ],
                "title": "Updated Title"
            }
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"
        assert len(response.json()["messages"]) == 2
    
    def test_delete_conversation(self):
        """Test deleting a conversation."""
        # Create
        conv_id = str(uuid.uuid4())
        client.post(
            "/api/v1/conversations/",
            headers=get_auth_headers(),
            json={"id": conv_id, "mode": "email", "title": "To Delete"}
        )
        
        # Delete
        response = client.delete(
            f"/api/v1/conversations/{conv_id}",
            headers=get_auth_headers()
        )
        assert response.status_code == 204
        
        # Verify deleted
        response = client.get(
            f"/api/v1/conversations/{conv_id}",
            headers=get_auth_headers()
        )
        assert response.status_code == 404
    
    def test_search_conversations(self):
        """Test searching conversations."""
        # Create a conversation with specific content
        conv_id = str(uuid.uuid4())
        client.post(
            "/api/v1/conversations/",
            headers=get_auth_headers(),
            json={"id": conv_id, "mode": "sql", "title": "Unique Search Term XYZ123"}
        )
        
        # Search for it
        response = client.get(
            "/api/v1/conversations/search/query?q=XYZ123",
            headers=get_auth_headers()
        )
        assert response.status_code == 200
        conversations = response.json()["conversations"]
        assert len(conversations) >= 1
        assert any("XYZ123" in c["title"] for c in conversations)


class TestFeedbackEndpoint:
    """Tests for feedback endpoint."""
    
    def test_submit_feedback(self):
        """Test submitting feedback."""
        response = client.post(
            "/api/v1/feedback/",
            json={
                "user_question": "What is the capital of France?",
                "agent_answer": "The capital of France is Paris.",
                "rating": "like",
                "reason": "Accurate answer"
            }
        )
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_submit_feedback_minimal(self):
        """Test submitting feedback with minimal data."""
        response = client.post(
            "/api/v1/feedback/",
            json={
                "user_question": "Test question",
                "agent_answer": "Test answer",
                "rating": "dislike"
            }
        )
        assert response.status_code == 200

