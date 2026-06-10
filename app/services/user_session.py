from sqlalchemy import select, func
from app.models.session import UserSession
from app.settings import settings
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


async def check_session_limit(db: AsyncSession, user_id):
    count_of_user_sessions = await db.scalar(
        select(func.count(UserSession.id)).where(UserSession.user_id == user_id)
    )
    if count_of_user_sessions > settings.MAX_USER_SESSION:
        raise HTTPException(429, detail="To many session for one user")
