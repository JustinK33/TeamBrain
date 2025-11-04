from app.db.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, func
from typing import Optional

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("Message", back_populates="user")
    memberships = relationship("SpaceMembership", back_populates="user")

class Space(Base):
    __tablename__ = "spaces"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    password_hash: Optional[str] = Column(String, nullable=True) # type: ignore

    messages = relationship("Message", back_populates="space")
    memberships = relationship("SpaceMembership", back_populates="space")

class SpaceMembership(Base):
    __tablename__ = "space_membership"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    space_id = Column(Integer, ForeignKey("spaces.id"), primary_key=True)
    join_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="memberships")
    space = relationship("Space", back_populates="memberships")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    content = Column(Text(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    space_id = Column(Integer, ForeignKey("spaces.id"))

    user = relationship("User", back_populates="messages")
    space = relationship("Space", back_populates="messages")