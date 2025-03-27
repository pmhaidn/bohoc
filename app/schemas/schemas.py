from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from ..models.models import UserRole

# User schemas
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

# Class schemas
class ClassBase(BaseModel):
    name: str
    academic_year: str
    description: Optional[str] = None

class ClassCreate(ClassBase):
    pass

class ClassUpdate(BaseModel):
    name: Optional[str] = None
    academic_year: Optional[str] = None
    description: Optional[str] = None

class Class(ClassBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Student schemas
class StudentBase(BaseModel):
    student_code: str
    full_name: str
    email: EmailStr
    phone: str
    address: str
    hometown: str
    id_card: str
    date_of_birth: datetime
    gender: str
    class_id: int
    
    # Thông tin học tập
    gpa: Optional[float] = None
    academic_status: Optional[str] = None
    accumulated_credits: Optional[int] = None
    study_status: Optional[str] = None
    
    # Thông tin liên hệ khẩn cấp
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    
    # Thông tin cá nhân bổ sung
    ethnicity: Optional[str] = None
    religion: Optional[str] = None
    nationality: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # Thông tin học vấn
    high_school: Optional[str] = None
    graduation_year: Optional[int] = None
    university_entrance_score: Optional[float] = None
    
    # Thông tin hoạt động
    extracurricular_activities: Optional[str] = None
    achievements: Optional[str] = None
    special_skills: Optional[str] = None

class StudentCreate(StudentBase):
    password: str  # For creating user account

class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    hometown: Optional[str] = None
    id_card: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    class_id: Optional[int] = None
    
    # Thông tin học tập
    gpa: Optional[float] = None
    academic_status: Optional[str] = None
    accumulated_credits: Optional[int] = None
    study_status: Optional[str] = None
    
    # Thông tin liên hệ khẩn cấp
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    
    # Thông tin cá nhân bổ sung
    ethnicity: Optional[str] = None
    religion: Optional[str] = None
    nationality: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # Thông tin học vấn
    high_school: Optional[str] = None
    graduation_year: Optional[int] = None
    university_entrance_score: Optional[float] = None
    
    # Thông tin hoạt động
    extracurricular_activities: Optional[str] = None
    achievements: Optional[str] = None
    special_skills: Optional[str] = None

class Student(StudentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    class_info: Optional[Class] = None

    class Config:
        from_attributes = True

class PaginatedStudentResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[Student]
    
    class Config:
        from_attributes = True

class StudentFilter(BaseModel):
    search: Optional[str] = None
    class_id: Optional[int] = None
    gender: Optional[str] = None
    academic_status: Optional[str] = None
    study_status: Optional[str] = None
    min_gpa: Optional[float] = None
    max_gpa: Optional[float] = None 