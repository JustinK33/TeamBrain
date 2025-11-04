from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import schemas, database
from app.db.models import SpaceMembership, Space, User
from app.core.security import get_current_user, hash_password, verify_password, create_access_token

router = APIRouter(prefix="/spaces", tags=["spaces"])

@router.post("/", response_model=schemas.SpaceResponse)
def create_space(space_data: schemas.SpaceCreate,
                 db: Session = Depends(database.get_db),
                 current_user: User = Depends(get_current_user)
                 ):
    new_space = Space(
        name=space_data.name,
        owner_id=current_user.id,
        description=space_data.description
    )
    if space_data.password_hash:
        hashed_password = hash_password(space_data.password_hash)
        new_space.password_hash = hashed_password
    db.add(new_space)
    db.commit()
    db.refresh(new_space)
    return new_space

@router.get("/", response_model=list[schemas.SpaceResponse])
def get_spaces(db: Session = Depends(database.get_db)):
    spaces = db.query(Space).all()
    return spaces

@router.post("/{space_id}/join", response_model=schemas.SpaceJoinResponse)
def join_space(space_id: int,
               join_data: schemas.SpaceJoinRequest,
               db: Session = Depends(database.get_db),
               current_user: User = Depends(get_current_user)               
               ):
    space = db.query(Space).filter(Space.id == space_id).first()
    if not space:
        raise HTTPException(status_code=404, detail="This space isnt found")

    if space.password_hash is not None:
        if join_data.password is None:
            raise HTTPException(status_code=403 or 401, detail="Password is required")
        if not verify_password(join_data.password, space.password_hash):
            raise HTTPException(status_code=401 or 403, detail="Wrong password")
        
    membership = db.query(SpaceMembership).filter(
        SpaceMembership.space_id == space_id,
        SpaceMembership.user_id == current_user.id
    ).first()
    if membership:
        raise HTTPException(status_code=400, detail="Already a member")
    
    new_member = SpaceMembership(user_id=current_user.id, space_id=space_id)
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return{
        "space_id": space_id,
        "joined": "true"
    }