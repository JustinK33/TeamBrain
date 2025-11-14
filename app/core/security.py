from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer
from app.db import models, database
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from app.db import schemas
import redis

rd = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        password = password[:72]
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire})
    # this works the opposite as payload in the get_current_user
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        # this works the opposite as payload in the create_access_token (breaking down the encode)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    key = f"user:{user_id}"
    
    try:
        cache = rd.get(key)
    except Exception:
        cache = None

    if cache is not None and isinstance(cache, str):
        cached = schemas.UserResponse.model_validate_json(cache)
        user = db.get(models.User, cached.id)
        if user:
            return user
        
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    try:
        rd.set(key, schemas.UserResponse.model_validate(user).model_dump_json(), ex=120)
    except:
        pass
    
    return user
