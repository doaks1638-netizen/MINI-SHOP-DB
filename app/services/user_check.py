from app.database import DBsession
from uuid import UUID
from app.models.user import User
from fastapi import HTTPException, Depends
from typing import Annotated
from sqlalchemy import select


async def check_user_exist(db: DBsession, user_id: UUID):
    user = await db.scalar(
        select(User).where(User.id == user_id).where(User.is_active == True)
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


type user_depens = Annotated[User, Depends(check_user_exist)]
