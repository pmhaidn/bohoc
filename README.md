# Student Management API

A FastAPI-based backend service for managing student information with authentication.

## Features

- JWT-based authentication
- Default admin account (username: admin, password: admin)
- CRUD operations for student information
- SQLite database
- API documentation with Swagger UI

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once the application is running, you can access:
- Swagger UI documentation: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

## API Endpoints

### Authentication
- POST `/api/v1/auth/token` - Login to get access token
- POST `/api/v1/auth/logout` - Logout

### Students
- GET `/api/v1/students/` - List all students
- GET `/api/v1/students/{student_id}` - Get student by ID
- POST `/api/v1/students/` - Create new student
- PUT `/api/v1/students/{student_id}` - Update student
- DELETE `/api/v1/students/{student_id}` - Delete student

## Authentication

To use the API, you need to:

1. Login using the default admin account:
   - Username: admin
   - Password: admin

2. Get the access token from the login response

3. Include the token in the Authorization header for all subsequent requests:
   ```
   Authorization: Bearer <your_access_token>
   ```

## Example Usage

1. Login to get token:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"
```

2. Create a new student:
```bash
curl -X POST "http://localhost:8000/api/v1/students/" \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "student_code": "ST001",
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "address": "123 Main St"
  }'
``` 