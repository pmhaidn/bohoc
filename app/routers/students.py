from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from ..core.database import get_db
from ..models import models
from ..schemas import schemas
from .auth import get_current_user
from ..core.security import get_password_hash
from math import ceil
from sqlalchemy import or_
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def check_admin_access(current_user: models.User):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

@router.post("/", response_model=schemas.Student)
def create_student(
    student: schemas.StudentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        check_admin_access(current_user)
        
        # Validate class_id
        if student.class_id is not None:
            # Check if class exists
            db_class = db.query(models.Class).filter(models.Class.id == student.class_id).first()
            if not db_class:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy lớp học với ID {student.class_id}"
                )
        
        # Create user account for student
        db_user = models.User(
            username=student.email,  # Using email as username
            hashed_password=get_password_hash(student.password),
            role=models.UserRole.STUDENT
        )
        db.add(db_user)
        
        # Create student profile
        student_data = student.dict(exclude={'password'})
        db_student = models.Student(**student_data)
        db.add(db_student)
        
        db.commit()
        db.refresh(db_student)
        return schemas.Student.from_orm(db_student)
    except HTTPException as he:
        raise he
    except IntegrityError as e:
        db.rollback()
        error_message = str(e)
        logger.error(f"IntegrityError when creating student: {error_message}")
        if "users_username_key" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được đăng ký cho tài khoản khác"
            )
        elif "students_email_key" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được đăng ký cho sinh viên khác"
            )
        elif "students_student_code_key" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã sinh viên đã tồn tại"
            )
        elif "students_id_card_key" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Số CCCD/CMND đã được đăng ký"
            )
        elif "students_class_id_fkey" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lớp học không tồn tại"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thông tin sinh viên không hợp lệ"
            )
    except Exception as e:
        db.rollback()
        error_message = str(e)
        error_traceback = traceback.format_exc()
        logger.error(f"Unexpected error when creating student: {error_message}\n{error_traceback}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi khi tạo sinh viên"
        )

@router.get("/", response_model=schemas.PaginatedStudentResponse)
def read_students(
    page: int = 1,
    page_size: int = 10,
    search: Optional[str] = None,
    class_id: Optional[int] = None,
    gender: Optional[str] = None,
    academic_status: Optional[str] = None,
    study_status: Optional[str] = None,
    min_gpa: Optional[float] = None,
    max_gpa: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        check_admin_access(current_user)
        
        # Đảm bảo page và page_size hợp lệ
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10
        
        # Tính toán skip
        skip = (page - 1) * page_size
        
        # Xây dựng query với các điều kiện lọc
        query = db.query(models.Student)
        
        # Áp dụng các bộ lọc
        if search:
            search = f"%{search}%"
            query = query.filter(
                or_(
                    models.Student.full_name.ilike(search),
                    models.Student.student_code.ilike(search),
                    models.Student.email.ilike(search)
                )
            )
        
        if class_id:
            query = query.filter(models.Student.class_id == class_id)
        
        if gender:
            query = query.filter(models.Student.gender == gender)
        
        if academic_status:
            query = query.filter(models.Student.academic_status == academic_status)
        
        if study_status:
            query = query.filter(models.Student.study_status == study_status)
        
        if min_gpa is not None:
            query = query.filter(models.Student.gpa >= min_gpa)
        
        if max_gpa is not None:
            query = query.filter(models.Student.gpa <= max_gpa)
        
        # Lấy tổng số học sinh sau khi áp dụng bộ lọc
        total = query.count()
        
        # Lấy danh sách học sinh theo trang
        students = query.offset(skip).limit(page_size).all()
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [schemas.Student.from_orm(student) for student in students]
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        error_message = str(e)
        error_traceback = traceback.format_exc()
        logger.error(f"Unexpected error when reading students: {error_message}\n{error_traceback}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi khi lấy danh sách sinh viên"
        )

@router.get("/{student_id}", response_model=schemas.Student)
def read_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        # Allow students to view their own profile
        if current_user.role == models.UserRole.STUDENT:
            student = db.query(models.Student).filter(models.Student.email == current_user.username).first()
            if student and student.id == student_id:
                return schemas.Student.from_orm(student)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền truy cập"
            )
        
        db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
        if db_student is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
        return schemas.Student.from_orm(db_student)
    except HTTPException as he:
        raise he
    except Exception as e:
        error_message = str(e)
        error_traceback = traceback.format_exc()
        logger.error(f"Unexpected error when reading student: {error_message}\n{error_traceback}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi khi lấy thông tin sinh viên"
        )

@router.put("/{student_id}", response_model=schemas.Student)
def update_student(
    student_id: int,
    student: schemas.StudentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        check_admin_access(current_user)
        
        db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
        if db_student is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
        
        # Check if class exists if class_id is provided
        student_data = student.dict(exclude_unset=True)
        if "class_id" in student_data:
            db_class = db.query(models.Class).filter(models.Class.id == student_data["class_id"]).first()
            if not db_class:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy lớp học với ID {student_data['class_id']}"
                )
        
        for key, value in student_data.items():
            setattr(db_student, key, value)
        
        db.commit()
        db.refresh(db_student)
        return schemas.Student.from_orm(db_student)
    except HTTPException as he:
        raise he
    except IntegrityError as e:
        db.rollback()
        error_message = str(e)
        logger.error(f"IntegrityError when updating student: {error_message}")
        if "students_email_key" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được đăng ký cho sinh viên khác"
            )
        elif "students_id_card_key" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Số CCCD/CMND đã được đăng ký"
            )
        elif "students_class_id_fkey" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lớp học không tồn tại"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thông tin sinh viên không hợp lệ"
            )
    except Exception as e:
        db.rollback()
        error_message = str(e)
        error_traceback = traceback.format_exc()
        logger.error(f"Unexpected error when updating student: {error_message}\n{error_traceback}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi khi cập nhật thông tin sinh viên"
        )

@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        check_admin_access(current_user)
        
        db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
        if db_student is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
        
        # Delete associated user account
        db_user = db.query(models.User).filter(models.User.username == db_student.email).first()
        if db_user:
            db.delete(db_user)
        
        db.delete(db_student)
        db.commit()
        return {"message": "Xóa sinh viên thành công"}
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        error_message = str(e)
        error_traceback = traceback.format_exc()
        logger.error(f"Unexpected error when deleting student: {error_message}\n{error_traceback}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi khi xóa sinh viên"
        ) 