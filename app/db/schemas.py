from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Annotated

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: Annotated[str, StringConstraints(min_length=8, max_length=72)]

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str