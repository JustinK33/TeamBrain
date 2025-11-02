from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import models, schemas, database
from app.core.security import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
def get_current_user_profile(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=schemas.UserResponse)
def update_user(update_data: schemas.UpdateUser,
                current_user: models.User = Depends(get_current_user),
                db: Session = Depends(database.get_db)
                ):
    if update_data.name is not None:
        current_user.name = update_data.name # type: ignore
    if update_data.email is not None:
        current_user.email = update_data.email # type: ignore

    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=list[schemas.UserResponse])
def get_all_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()
    # since i have orm_mode=True in settings it returns JSON formatted
    return users