from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict
from typing import Annotated, Optional, Text
from datetime import datetime

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

    model_config = ConfigDict(from_attributes=True)

class UpdateUser(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class SpaceBase(BaseModel):
    name: str
    description: Optional[str] = None

class SpaceCreate(SpaceBase):
    password_hash: Optional[str] = None

class SpaceMembershipResponse(BaseModel):
    name: str
    id: int

    model_config = ConfigDict(from_attributes=True)

class SpaceResponse(SpaceBase):
    id: int
    owner_id: int
    requires_password: bool

    model_config = ConfigDict(from_attributes=True)

class SpaceJoinRequest(BaseModel):
    password: Optional[str] = None

class SpaceJoinResponse(BaseModel):
    space_id: int
    joined: bool

    class Config:
        orm_mode = True

class CreateMessage(BaseModel):
    content: str
    space_id: int

class MessageResponse(BaseModel):
    id: int
    content: str
    user_id: int
    space_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MessgeEditResponse(BaseModel):
    id: int
    content: str
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class UpdateMessage(BaseModel):
    content: str

    model_config = ConfigDict(from_attributes=True)