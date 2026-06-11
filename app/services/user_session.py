from sqlalchemy import select, func
from app.models.session import UserSession
from app.settings import settings
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


async def check_session_limit(db: AsyncSession, user_id):
    count_of_user_sessions = await db.scalar(
        select(func.count(UserSession.id)).where(
            UserSession.user_id == user_id, UserSession.is_active == True
        )
    )
    if count_of_user_sessions >= settings.MAX_USER_SESSION:
        raise HTTPException(429, detail="Too many sessions for one user")
