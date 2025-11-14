from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password, create_access_token
from app.db.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from app.db.models import User
from datetime import timedelta
from slowapi import Limiter
from app.core.config import settings
from slowapi.util import get_remote_address

router = APIRouter(prefix="/auth", tags=['auth'])

limiter = Limiter(key_func=get_remote_address,
                  storage_uri=settings.REDIS_URL
                  )

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    exisiting_email = db.query(User).filter(User.email == user_data.email).first()
    if exisiting_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = hash_password(user_data.password)
    user = User(name=user_data.name, email=user_data.email, password_hash=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# learn this
@router.post("/login", response_model=TokenResponse)
@limiter.limit("3/minute", per_method=True)
def login(user_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    if not verify_password(user_data.password, user.password_hash): # type: ignore
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(minutes=60)
    refresh_token = create_access_token(
        data={"sub": str(user.id), "type": "refresh"}, expires_delta=refresh_token_expires
    )
    return {"access_token": access_token, "refresh_token": refresh_token,  "token_type": "bearer"}