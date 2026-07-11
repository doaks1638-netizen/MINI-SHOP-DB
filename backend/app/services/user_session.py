from sqlalchemy import select, func
from app.models import UserSession
from app.core.settings import settings
from sqlalchemy.ext.asyncio import AsyncSession


async def check_session_limit(db: AsyncSession, user_id):
    count_of_user_sessions = await db.scalar(
        select(func.count(UserSession.id)).where(
            UserSession.user_id == user_id, UserSession.is_active == True
        )
    )
    if count_of_user_sessions >= settings.JWT_MAX_USER_SESSION:
        oldest_sessions = await db.scalars(
            select(UserSession)
            .where(UserSession.user_id == user_id, UserSession.is_active == True)
            .order_by(UserSession.expiration_time)
            .limit(count_of_user_sessions - settings.JWT_MAX_USER_SESSION + 1)
        )
        for session in oldest_sessions:
            session.is_active = False
        await db.flush()
