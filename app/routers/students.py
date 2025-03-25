from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from ..core.database import get_db
from ..models import models
from ..schemas import schemas
from .auth import get_current_user
from math import ceil

router = APIRouter()

@router.post("/", response_model=schemas.Student)
def create_student(
    student: schemas.StudentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        db_student = models.Student(**student.dict())
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return schemas.Student.from_orm(db_student)
    except IntegrityError as e:
        db.rollback()
        if "students_email_key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        elif "students_student_code_key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student code already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A student with this information already exists"
            )

@router.get("/", response_model=schemas.PaginatedStudentResponse)
def read_students(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Đảm bảo page và page_size hợp lệ
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    
    # Tính toán skip
    skip = (page - 1) * page_size
    
    # Lấy tổng số học sinh
    total = db.query(models.Student).count()
    
    # Lấy danh sách học sinh theo trang
    students = db.query(models.Student).offset(skip).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [schemas.Student.from_orm(student) for student in students]
    }

@router.get("/{student_id}", response_model=schemas.Student)
def read_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return schemas.Student.from_orm(db_student)

@router.put("/{student_id}", response_model=schemas.Student)
def update_student(
    student_id: int,
    student: schemas.StudentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
        if db_student is None:
            raise HTTPException(status_code=404, detail="Student not found")
        
        for key, value in student.dict(exclude_unset=True).items():
            setattr(db_student, key, value)
        
        db.commit()
        db.refresh(db_student)
        return schemas.Student.from_orm(db_student)
    except IntegrityError as e:
        db.rollback()
        if "students_email_key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        elif "students_student_code_key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student code already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A student with this information already exists"
            )

@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(db_student)
    db.commit()
    return {"message": "Student deleted successfully"} 