import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db
from app.models import models
from app.schemas.schemas import UserRole
from app.core.security import get_password_hash

# Create test database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=30
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db():
    # Drop all tables first
    models.Base.metadata.drop_all(bind=engine)
    # Create test database tables
    models.Base.metadata.create_all(bind=engine)
    
    # Override the get_db dependency
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield
    # Clean up after tests
    try:
        models.Base.metadata.drop_all(bind=engine)
    except Exception as e:
        print(f"Error dropping tables: {e}")
    # Clear dependency overrides
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def client():
    return TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
        session.rollback()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

@pytest.fixture(scope="function")
def admin_user(test_db, db_session):
    print("\nCreating admin user...")  # Debug log
    
    # Delete existing admin user if exists
    existing_user = db_session.query(models.User).filter(models.User.username == "admin").first()
    if existing_user:
        print(f"Found existing admin user: {existing_user.username}, {existing_user.is_active}, {existing_user.role}")  # Debug log
        db_session.delete(existing_user)
        db_session.commit()
    
    # Create new admin user
    admin = models.User(
        username="admin",
        hashed_password=get_password_hash("admin"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    
    # Verify user was created
    user = db_session.query(models.User).filter(models.User.username == "admin").first()
    print(f"Created admin user: {user.username}, {user.is_active}, {user.role}")  # Debug log
    assert user is not None
    assert user.is_active
    assert user.role == UserRole.ADMIN
    
    return admin

@pytest.fixture(scope="function")
def admin_token(client, admin_user, db_session):
    print("\nGetting admin token...")  # Debug log
    
    # First verify admin user exists
    user = db_session.query(models.User).filter(models.User.username == "admin").first()
    print(f"Verifying admin user exists: {user.username if user else None}, {user.is_active if user else None}, {user.role if user else None}")  # Debug log
    assert user is not None
    assert user.is_active
    assert user.role == UserRole.ADMIN
    
    # Get token
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print(f"Admin token response: {response.status_code} - {response.text}")  # Debug log
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture(scope="function")
def test_class(test_db, db_session):
    # Delete existing test class if exists
    db_session.query(models.Class).filter(models.Class.name == "Test Class").delete()
    db_session.commit()
    
    # Create new test class
    class_data = models.Class(
        name="Test Class",
        academic_year="2023-2024",
        description="Test Class Description"
    )
    db_session.add(class_data)
    db_session.commit()
    db_session.refresh(class_data)
    return class_data 