import pytest

def test_create_doctor_as_admin_success(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "user": {
            "email": "doctor@medsync.com",
            "password": "docpassword123",
            "role": "DOCTOR"
        },
        "name": "Gregory House",
        "crm": "123456-SP"
    }
    response = client.post("/clinic/doctors", json=payload, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Gregory House"
    assert data["crm"] == "123456-SP"
    assert "password" not in data["user"]

def test_create_doctor_unauthorized_token(client):
    payload = {
            "user": {
                "email": "doctor@medsync.com",
                "password": "docpassword123",
                "role": "DOCTOR"
            },
            "name": "Dr. Gregory House",
            "crm": "123456-SP"
    }
    response = client.post("/clinic/doctors", json=payload)

    assert response.status_code == 401