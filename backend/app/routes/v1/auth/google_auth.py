from fastapi import APIRouter, Depends, Request
from app.db.database import DBsession
from app.services import (
    create_tokens,
    check_session_limit,
)
from sqlalchemy import select
from uuid6 import uuid7
from datetime import datetime, timezone
from app.core.settings import settings
from typing import Annotated
from fastapi_sso import GoogleSSO
from fastapi.responses import RedirectResponse
from app.models.enums import UserStatus
from app.models import User, UserSession
from app.core.limiter import limiter

google_router = APIRouter(prefix="/google", tags=["GOOGLE"])


async def get_google_sso():
    sso = GoogleSSO(
        settings.JWT_CLIENT_ID, settings.JWT_CLIENT_SECRET, settings.JWT_REDIRECT_URL
    )
    async with sso:
        yield sso


@google_router.get("/login")
@limiter.limit("100/day")
async def google_login(request: Request, sso: Annotated[GoogleSSO, Depends(get_google_sso)]):
    return await sso.get_login_redirect()


@google_router.get("/callback")
async def google_callback(
    sso: Annotated[GoogleSSO, Depends(get_google_sso)], request: Request, db: DBsession
):

    try:
        google_user = await sso.verify_and_process(request)
    except Exception:
        return RedirectResponse("/login?error=auth_failed")

    same_user_stmt = select(User).where(User.email == google_user.email)
    same_user = await db.scalar(same_user_stmt)
    if same_user:
        # User already exists (make session)
        await check_session_limit(db=db, user_id=same_user.id)

        same_user.picture = google_user.picture
        same_user.name = google_user.display_name

        if same_user.status != UserStatus.active:
            same_user.status = UserStatus.active

        current_user = same_user

    else:
        current_user = User(
            google_id=google_user.id,
            name=google_user.display_name,
            email=google_user.email,
            picture=google_user.picture,
        )
        db.add(current_user)
        await db.flush()

    token_id = uuid7()

    new_session = UserSession(
        user_id=current_user.id,
        active_token_id=token_id,
        expiration_time=datetime.now(timezone.utc) + settings.JWT_REFRESH_TOKEN_TIME,
    )
    db.add(new_session)

    await db.flush()

    refresh_data = {
        "sub": str(current_user.id),
        "session_id": str(new_session.id),
        "token_id": str(token_id),
    }

    access_data = {"sub": str(current_user.id)}

    tokens = create_tokens(access_data, refresh_data)

    await db.commit()

    return RedirectResponse(
        f"/callback?access_token={tokens['access_token']}&refresh_token={tokens['refresh_token']}"
    )
