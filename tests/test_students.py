import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime
from app.main import app
from app.core.database import get_db
from app.models import models
from app.schemas.schemas import UserRole

client = TestClient(app)

# Test data
test_student_data = {
    "student_code": "ST001",
    "full_name": "Test Student",
    "email": "test@example.com",
    "phone": "0123456789",
    "address": "Test Address",
    "hometown": "Test Hometown",
    "id_card": "123456789",
    "date_of_birth": datetime.now().isoformat(),
    "gender": "Nam",
    "password": "testpassword123"
}

test_class_data = {
    "name": "Test Class",
    "academic_year": "2023-2024",
    "description": "Test Class Description"
}

@pytest.fixture
def test_db():
    # Create test database
    from app.core.database import engine
    models.Base.metadata.create_all(bind=engine)
    yield
    # Clean up after tests
    models.Base.metadata.drop_all(bind=engine)

@pytest.fixture
def admin_token(test_db):
    # Create admin user and get token
    from app.core.security import get_password_hash
    db = next(get_db())
    admin = models.User(
        username="admin",
        hashed_password=get_password_hash("admin"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin)
    db.commit()
    
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin"}
    )
    return response.json()["access_token"]

@pytest.fixture
def test_class(test_db):
    db = next(get_db())
    # Delete existing test class if exists
    db.query(models.Class).filter(models.Class.name == test_class_data["name"]).delete()
    db.commit()
    
    # Create new test class
    class_data = models.Class(**test_class_data)
    db.add(class_data)
    db.commit()
    db.refresh(class_data)
    return class_data

def test_create_student(test_db, admin_token, test_class):
    student_data = test_student_data.copy()
    student_data["class_id"] = test_class.id
    response = client.post(
        "/api/v1/students/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=student_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["student_code"] == test_student_data["student_code"]
    assert data["full_name"] == test_student_data["full_name"]
    assert data["email"] == test_student_data["email"]

def test_create_student_duplicate_email(test_db, admin_token, test_class):
    student_data = test_student_data.copy()
    student_data["class_id"] = test_class.id
    # Create first student
    client.post(
        "/api/v1/students/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=student_data
    )
    
    # Try to create second student with same email
    response = client.post(
        "/api/v1/students/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=student_data
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_get_students(test_db, admin_token, test_class):
    # Create a student first
    student_data = test_student_data.copy()
    student_data["class_id"] = test_class.id
    client.post(
        "/api/v1/students/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=student_data
    )
    
    # Test getting students with filters
    response = client.get(
        "/api/v1/students/",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={
            "search": "Test",
            "class_id": test_class.id,
            "gender": "Nam",
            "page": 1,
            "page_size": 10
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    assert len(data["items"]) > 0
    assert data["page"] == 1
    assert data["page_size"] == 10

def test_get_student_by_id(test_db, admin_token, test_class):
    # Create a student first
    student_data = test_student_data.copy()
    student_data["class_id"] = test_class.id
    create_response = client.post(
        "/api/v1/students/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=student_data
    )
    student_id = create_response.json()["id"]
    
    # Test getting student by ID
    response = client.get(
        f"/api/v1/students/{student_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == student_id

def test_update_student(test_db, admin_token, test_class):
    # Create a student first
    student_data = test_student_data.copy()
    student_data["class_id"] = test_class.id
    create_response = client.post(
        "/api/v1/students/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=student_data
    )
    student_id = create_response.json()["id"]
    
    # Update student
    update_data = {
        "full_name": "Updated Name",
        "phone": "9876543210"
    }
    response = client.put(
        f"/api/v1/students/{student_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["phone"] == update_data["phone"]

def test_delete_student(test_db, admin_token, test_class):
    # Create a student first
    student_data = test_student_data.copy()
    student_data["class_id"] = test_class.id
    create_response = client.post(
        "/api/v1/students/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=student_data
    )
    student_id = create_response.json()["id"]
    
    # Delete student
    response = client.delete(
        f"/api/v1/students/{student_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    # Verify student is deleted
    get_response = client.get(
        f"/api/v1/students/{student_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert get_response.status_code == 404

def test_unauthorized_access(test_db, test_class):
    # Test accessing endpoints without token
    response = client.get("/api/v1/students/")
    assert response.status_code == 401

def test_student_access_own_profile(test_db, admin_token, test_class):
    # Create a student
    student_data = test_student_data.copy()
    student_data["class_id"] = test_class.id
    create_response = client.post(
        "/api/v1/students/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=student_data
    )
    student_id = create_response.json()["id"]
    
    # Create student user and get token
    student_token_response = client.post(
        "/api/v1/auth/token",
        data={"username": test_student_data["email"], "password": test_student_data["password"]}
    )
    student_token = student_token_response.json()["access_token"]
    
    # Test student accessing own profile
    response = client.get(
        f"/api/v1/students/{student_id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    
    # Test student accessing other student's profile
    other_student_data = test_student_data.copy()
    other_student_data["email"] = "other@example.com"
    other_student_data["student_code"] = "ST002"
    other_student_data["id_card"] = "987654321"
    other_student_data["class_id"] = test_class.id
    
    create_other_response = client.post(
        "/api/v1/students/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=other_student_data
    )
    other_student_id = create_other_response.json()["id"]
    
    response = client.get(
        f"/api/v1/students/{other_student_id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 403

def test_create_student_invalid_class_id(test_db, admin_token):
    student_data = test_student_data.copy()
    student_data["class_id"] = 99999  # Non-existent class ID
    response = client.post(
        "/api/v1/students/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=student_data
    )
    assert response.status_code == 404
    assert "Class not found" in response.json()["detail"]

def test_update_student_invalid_class_id(test_db, admin_token, test_class):
    # Create a student first
    student_data = test_student_data.copy()
    student_data["class_id"] = test_class.id
    create_response = client.post(
        "/api/v1/students/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=student_data
    )
    student_id = create_response.json()["id"]
    
    # Try to update student with invalid class_id
    update_data = {
        "class_id": 99999  # Non-existent class ID
    }
    response = client.put(
        f"/api/v1/students/{student_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=update_data
    )
    assert response.status_code == 404
    assert "Class not found" in response.json()["detail"] 