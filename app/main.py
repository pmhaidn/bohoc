from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import engine, get_db
from .models import models
from .routers import auth, students
from .core.security import get_password_hash
from sqlalchemy.orm import Session

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR + "/auth", tags=["auth"])
app.include_router(students.router, prefix=settings.API_V1_STR + "/students", tags=["students"])

# Create default admin user
def create_default_admin():
    db = next(get_db())
    admin = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin:
        admin = models.User(
            username="admin",
            hashed_password=get_password_hash("admin"),
            is_active=True
        )
        db.add(admin)
        db.commit()

@app.on_event("startup")
async def startup_event():
    create_default_admin()

@app.get("/")
async def root():
    return {"message": "Welcome to Student Management API"} 