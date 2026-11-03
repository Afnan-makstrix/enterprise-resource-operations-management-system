"""
Authentication, Identity & Role-Based Access Control Tests
"""
import pytest
from fastapi import status

def test_login_successful(client):
    """Verifies that valid username and password yield a JWT bearer token."""
    response = client.post(
        "/api/v1/auth/json-login",
        json={"username": "admin_tester", "password": "TestPassword123!"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["username"] == "admin_tester"
    assert data["role"] == "Super Admin"

def test_login_invalid_password(client):
    """Verifies that invalid password returns 401 Unauthorized."""
    response = client.post(
        "/api/v1/auth/json-login",
        json={"username": "admin_tester", "password": "WrongPassword!"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_login_nonexistent_user(client):
    """Verifies that non-existent username returns 401 Unauthorized."""
    response = client.post(
        "/api/v1/auth/json-login",
        json={"username": "non_existent_ghost", "password": "Password123!"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_protected_route_unauthorized_without_token(client):
    """Protected endpoints must reject requests lacking Authorization Bearer header."""
    response = client.get("/api/v1/employees/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_current_user_profile_endpoint(client, auth_headers):
    """Authenticated user can fetch their personal employee profile via /auth/me."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "admin.tester@eroms-test.com"
    assert data["role_name"] == "Super Admin"
