import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db
from app.models import models
from app.schemas.schemas import UserRole

client = TestClient(app)

# Test data
test_class_data = {
    "name": "Test Class",
    "academic_year": "2023-2024",
    "description": "Test Class Description"
}

def test_create_class(test_db, admin_token):
    response = client.post(
        "/api/v1/classes/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=test_class_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_class_data["name"]
    assert data["academic_year"] == test_class_data["academic_year"]
    assert data["description"] == test_class_data["description"]

def test_create_class_duplicate_name(test_db, admin_token):
    # Create first class
    client.post(
        "/api/v1/classes/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=test_class_data
    )
    
    # Try to create second class with same name
    response = client.post(
        "/api/v1/classes/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=test_class_data
    )
    assert response.status_code == 400

def test_get_classes(test_db, admin_token):
    # Create a class first
    client.post(
        "/api/v1/classes/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=test_class_data
    )
    
    # Test getting all classes
    response = client.get(
        "/api/v1/classes/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == test_class_data["name"]

def test_get_class_by_id(test_db, admin_token):
    # Create a class first
    create_response = client.post(
        "/api/v1/classes/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=test_class_data
    )
    class_id = create_response.json()["id"]
    
    # Test getting class by ID
    response = client.get(
        f"/api/v1/classes/{class_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == class_id

def test_update_class(test_db, admin_token):
    # Create a class first
    create_response = client.post(
        "/api/v1/classes/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=test_class_data
    )
    class_id = create_response.json()["id"]
    
    # Update class
    update_data = {
        "name": "Updated Class Name",
        "description": "Updated Description"
    }
    response = client.put(
        f"/api/v1/classes/{class_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]

def test_delete_class(test_db, admin_token):
    # Create a class first
    create_response = client.post(
        "/api/v1/classes/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=test_class_data
    )
    class_id = create_response.json()["id"]
    
    # Delete class
    response = client.delete(
        f"/api/v1/classes/{class_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    # Verify class is deleted
    get_response = client.get(
        f"/api/v1/classes/{class_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert get_response.status_code == 404

def test_delete_class_with_students(test_db, admin_token):
    # Create a class first
    create_response = client.post(
        "/api/v1/classes/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=test_class_data
    )
    class_id = create_response.json()["id"]
    
    # Create a student in this class
    test_student_data = {
        "student_code": "ST001",
        "full_name": "Test Student",
        "email": "test@example.com",
        "phone": "0123456789",
        "address": "Test Address",
        "hometown": "Test Hometown",
        "id_card": "123456789",
        "date_of_birth": "2000-01-01T00:00:00",
        "gender": "Nam",
        "class_id": class_id,
        "password": "testpassword123"
    }
    
    client.post(
        "/api/v1/students/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=test_student_data
    )
    
    # Try to delete class with students
    response = client.delete(
        f"/api/v1/classes/{class_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400
    assert "Cannot delete class with existing students" in response.json()["detail"]

def test_unauthorized_access(test_db):
    # Test accessing endpoints without token
    response = client.get("/api/v1/classes/")
    assert response.status_code == 401 