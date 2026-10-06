from fastapi import status

def test_register_student_success(client):
    payload = {
        "campus_id": "STU-NEW-999",
        "full_name": "Rohan Verma",
        "email": "rohan@campus.edu",
        "password": "securepassword123",
        "role": "STUDENT",
        "phone": "+91 91234 56789"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "rohan@campus.edu"
    assert data["user"]["role"] == "STUDENT"

def test_register_duplicate_email(client):
    payload = {
        "campus_id": "STU-DUP-001",
        "full_name": "Duplicate Student",
        "email": "student@test.com", # Already seeded in conftest
        "password": "password123"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]

def test_login_success(client):
    payload = {
        "email": "student@test.com",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "student@test.com"

def test_login_invalid_password(client):
    payload = {
        "email": "student@test.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_rbac_admin_endpoint_forbidden_for_student(client, student_auth_headers):
    # Student attempting to view admin bottlenecks
    response = client.get("/api/v1/admin/bottlenecks", headers=student_auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
