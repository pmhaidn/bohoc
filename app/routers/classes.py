from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from ..core.database import get_db
from ..models import models
from ..schemas import schemas
from .auth import get_current_user
from .students import check_admin_access

router = APIRouter()

@router.post("/", response_model=schemas.Class)
def create_class(
    class_data: schemas.ClassCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    check_admin_access(current_user)
    
    try:
        db_class = models.Class(**class_data.dict())
        db.add(db_class)
        db.commit()
        db.refresh(db_class)
        return schemas.Class.from_orm(db_class)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A class with this information already exists"
        )

@router.get("/", response_model=List[schemas.Class])
def read_classes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    classes = db.query(models.Class).all()
    return [schemas.Class.from_orm(class_) for class_ in classes]

@router.get("/{class_id}", response_model=schemas.Class)
def read_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_class = db.query(models.Class).filter(models.Class.id == class_id).first()
    if db_class is None:
        raise HTTPException(status_code=404, detail="Class not found")
    return schemas.Class.from_orm(db_class)

@router.put("/{class_id}", response_model=schemas.Class)
def update_class(
    class_id: int,
    class_data: schemas.ClassUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    check_admin_access(current_user)
    
    try:
        db_class = db.query(models.Class).filter(models.Class.id == class_id).first()
        if db_class is None:
            raise HTTPException(status_code=404, detail="Class not found")
        
        for key, value in class_data.dict(exclude_unset=True).items():
            setattr(db_class, key, value)
        
        db.commit()
        db.refresh(db_class)
        return schemas.Class.from_orm(db_class)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A class with this information already exists"
        )

@router.delete("/{class_id}")
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    check_admin_access(current_user)
    
    db_class = db.query(models.Class).filter(models.Class.id == class_id).first()
    if db_class is None:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Check if there are any students in this class
    if db.query(models.Student).filter(models.Student.class_id == class_id).count() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete class with existing students"
        )
    
    db.delete(db_class)
    db.commit()
    return {"message": "Class deleted successfully"} 