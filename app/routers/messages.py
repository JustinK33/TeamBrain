from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import delete
from app.db.schemas import MessageResponse, CreateMessage, MessgeEditResponse, UpdateMessage
from app.db.models import User, Message, SpaceMembership, Space
from app.db import database
from app.core.security import get_current_user, get_userid_from_request
from app.core.config import settings

from slowapi import Limiter
from slowapi.util import get_remote_address

def limit_by_user(request: Request):
    user_id = get_userid_from_request(request)
    if user_id is not None:
        return(f"user:{user_id}")
    return(f"ip:{get_remote_address(request)}")

limiter = Limiter(key_func=limit_by_user,
                  storage_uri=settings.REDIS_URL
                  )

router = APIRouter(prefix="/messages", tags=['messages'])

@router.post("/", response_model=MessageResponse)
@limiter.limit("1/minute", per_method=True)
def create_message(message_data: CreateMessage,
                   request: Request, # i need this bc the docs said so
                   current_user: User = Depends(get_current_user),
                   db: Session = Depends(database.get_db)
                   ) -> Message:
    space_exist = db.query(Space).filter(Space.id == message_data.space_id).first()
    if not space_exist:
        raise HTTPException(status_code=404, detail="This space does not exists")
    new_content = Message(
        user_id=current_user.id,
        content=message_data.content,
        space_id=message_data.space_id
    )
    is_member = db.query(SpaceMembership).filter(
        SpaceMembership.user_id == current_user.id,
        SpaceMembership.space_id == message_data.space_id
    ).first()
    if not is_member:
        raise HTTPException(status_code=403, detail="You're not a member of this space")
    if len(message_data.content) > 200:
        raise HTTPException(status_code=400, detail="Message exceeds limit: 200")
    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    return new_content

@router.get("/")
def get_messages(space_id: int, db: Session = Depends(database.get_db)):
    if space_id:
        messages = db.query(Message).filter(Message.space_id == space_id).all()
    else:
        messages = db.query(Message).all()
    return messages

@router.get("/{id}", response_model=MessageResponse)
def get_message(id: int, db: Session = Depends(database.get_db)):
    message = db.query(Message).filter(Message.id == id).first()
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.delete("/{id}")
def delete_message(id: int, 
                   db: Session = Depends(database.get_db),
                   current_user: User = Depends(get_current_user)
                   ):
    message = db.query(Message).filter(Message.user_id == current_user.id,
                                       Message.id == id).first()
    if not message:
        raise HTTPException(status_code=400, detail="This isn't your message")
    db.delete(message)
    db.commit()
    return{
        "delete": "complete"
    }

@router.put("/{message_id}", response_model=MessgeEditResponse)
def edit_message(new_content: UpdateMessage,
                 message_id: int,
                 db: Session = Depends(database.get_db),
                 current_user: User = Depends(get_current_user)
                 ):
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.user_id == current_user.id
    ).first()
    if message is None:
        raise HTTPException(status_code=404, detail="Message doesn't exists")
    if new_content is not None:
        message.content = new_content.content # type: ignore

    db.commit()
    db.refresh(message)
    return message
