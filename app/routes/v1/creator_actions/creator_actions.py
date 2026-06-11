from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from app.routes.dependencies import get_current_creator
from app.schemas import FullUserCreate, UserDTO
from app.database import DBsession
from app.models.user import User
from app.services import create_hash_password

creator_router = APIRouter(
    prefix="/creator", dependencies=[Depends(get_current_creator)], tags=["CREATOR"]
)


@creator_router.post("/users", response_model=UserDTO)
async def create_user(db: DBsession, new_user: FullUserCreate):
    same_user = select(User).where(User.email == new_user.email)
    if await db.scalar(same_user):
        raise HTTPException(400, detail="User already exists")
    new_user = User(
        name=new_user.name,
        email=new_user.email,
        hash_password=create_hash_password(new_user.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
