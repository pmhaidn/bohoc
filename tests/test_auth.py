import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db
from app.models import models
from app.schemas.schemas import UserRole
from app.core.security import get_password_hash

def test_login_success(test_db, admin_user, client, db_session):
    # Verify admin user exists in database
    user = db_session.query(models.User).filter(models.User.username == "admin").first()
    print(f"Verifying admin user exists: {user.username if user else None}, {user.is_active if user else None}, {user.role if user else None}")  # Debug log
    assert user is not None
    assert user.is_active
    assert user.role == UserRole.ADMIN
    
    # Test login
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print(f"Login response: {response.status_code} - {response.text}")  # Debug log
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(test_db, admin_user, client, db_session):
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_login_nonexistent_user(test_db, client, db_session):
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "nonexistent", "password": "password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_login_inactive_user(test_db, client, db_session):
    # Create inactive user
    inactive_user = models.User(
        username="inactive",
        hashed_password=get_password_hash("password"),
        role=UserRole.STUDENT,
        is_active=False
    )
    db_session.add(inactive_user)
    db_session.commit()
    
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "inactive", "password": "password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
    assert "Inactive user" in response.json()["detail"]

def test_logout_success(test_db, admin_user, client):
    # First login to get token
    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Then logout
    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"

def test_logout_invalid_token(test_db, client):
    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401

def test_logout_no_token(test_db, client):
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 401

def test_change_password_success(test_db, admin_user, client):
    # First login to get token
    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Change password
    response = client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "admin",
            "new_password": "newpassword123"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"
    
    # Verify can login with new password
    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "newpassword123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert login_response.status_code == 200

def test_change_password_wrong_current_password(test_db, admin_user, client, db_session):
    # First login to get token
    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print(f"Login response: {login_response.status_code} - {login_response.text}")  # Debug log
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Try to change password with wrong current password
    response = client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
    )
    print(f"Change password response: {response.status_code} - {response.text}")  # Debug log
    assert response.status_code == 400
    assert "Incorrect current password" in response.json()["detail"]

def test_change_password_invalid_token(test_db, client):
    response = client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": "Bearer invalid_token"},
        json={
            "current_password": "admin",
            "new_password": "newpassword123"
        }
    )
    assert response.status_code == 401 