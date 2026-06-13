from app.models import User
from app.database import DBsession
from uuid import UUID
from fastapi import HTTPException, Depends
from typing import Annotated
from sqlalchemy import select


async def check_user_exist(db: DBsession, user_id: UUID):
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


type user_depends = Annotated[User, Depends(check_user_exist)]
