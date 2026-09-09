from __future__ import annotations


def test_no_default_admin_account(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 401


def test_provisioned_user_can_login_and_verify(client, demo_credentials):
    username, password = demo_credentials
    login = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["username"] == username

    verify = client.post("/api/v1/auth/verify", headers=headers)
    assert verify.status_code == 200
    assert verify.json()["valid"] is True


def test_authentication_rejects_missing_or_invalid_token(client):
    assert client.get("/api/v1/auth/me").status_code == 401
    assert client.post("/api/v1/auth/verify", headers={"Authorization": "Bearer invalid"}).status_code == 401
