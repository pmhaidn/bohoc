from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STUDENT = "student"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    academic_year = Column(String)  # e.g., "2023-2024"
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    students = relationship("Student", back_populates="class_info")

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_code = Column(String, unique=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    address = Column(String)
    hometown = Column(String)  # Quê quán
    id_card = Column(String, unique=True)  # CCCD
    date_of_birth = Column(DateTime(timezone=True))
    gender = Column(String)  # Nam/Nữ
    class_id = Column(Integer, ForeignKey("classes.id"))
    
    # Thông tin học tập
    gpa = Column(Float, nullable=True)  # Điểm trung bình học tập
    academic_status = Column(String, nullable=True)  # Học lực
    accumulated_credits = Column(Integer, nullable=True)  # Số tín chỉ đã tích lũy
    study_status = Column(String, nullable=True)  # Trạng thái học tập
    
    # Thông tin liên hệ khẩn cấp
    emergency_contact_name = Column(String, nullable=True)  # Tên người thân
    emergency_contact_phone = Column(String, nullable=True)  # Số điện thoại người thân
    emergency_contact_relation = Column(String, nullable=True)  # Mối quan hệ
    
    # Thông tin cá nhân bổ sung
    ethnicity = Column(String, nullable=True)  # Dân tộc
    religion = Column(String, nullable=True)  # Tôn giáo
    nationality = Column(String, nullable=True)  # Quốc tịch
    avatar_url = Column(String, nullable=True)  # Ảnh đại diện
    
    # Thông tin học vấn
    high_school = Column(String, nullable=True)  # Trường THPT
    graduation_year = Column(Integer, nullable=True)  # Năm tốt nghiệp THPT
    university_entrance_score = Column(Float, nullable=True)  # Điểm thi đại học
    
    # Thông tin hoạt động
    extracurricular_activities = Column(String, nullable=True)  # Hoạt động ngoại khóa
    achievements = Column(String, nullable=True)  # Thành tích
    special_skills = Column(String, nullable=True)  # Kỹ năng đặc biệt
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    class_info = relationship("Class", back_populates="students") 