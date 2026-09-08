import pytest

def test_login_success(client, admin_user):
    response = client.post(
        "auth/login",
        data={"username": "admin@medsync.com", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client, admin_user):
    response = client.post(
        "auth/login",
        data={"username": "admin@medsync.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password."
