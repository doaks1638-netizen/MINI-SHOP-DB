from fastapi import APIRouter, HTTPException, Depends, Request
from app.database import DBsession
from app.routes import (
    exc,
)
from app.schemas import (
    TokenResponse,
    RefreshToken,
)
from app.models.user import User
from app.models.session import UserSession
from app.services import (
    create_tokens,
    decode_refresh_token,
    check_session_limit,
)
from sqlalchemy import select
from uuid import UUID
from uuid6 import uuid7
from datetime import datetime, timezone
from app.settings import settings
from typing import Annotated
from fastapi_sso import GoogleSSO
from app.settings import settings

auth_router = APIRouter(prefix="/auth", tags=["AUTHENTICATION"])
google_router = APIRouter(prefix="/google", tags=["GOOGLE"])


async def get_google_sso():
    sso = GoogleSSO(settings.CLIENT_ID, settings.CLIENT_SECRET, settings.REDIRECT_URL)
    async with sso:
        yield sso


@google_router.get("/login")
async def google_login(sso: Annotated[GoogleSSO, Depends(get_google_sso)]):
    return await sso.get_login_redirect()


@google_router.get("/callback")
async def google_callback(
    sso: Annotated[GoogleSSO, Depends(get_google_sso)], request: Request, db: DBsession
):
    try:
        google_user = await sso.verify_and_process(request)
    except Exception:
        raise HTTPException(403, detail="Failed to verify user")

    same_user_stmt = select(User).where(User.email == google_user.email)
    same_user = await db.scalar(same_user_stmt)
    if same_user:
        # User already exists (make session)
        await check_session_limit(db=db, user_id=same_user.id)

        same_user.picture = google_user.picture
        same_user.name = google_user.display_name

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
        expiration_time=datetime.now(timezone.utc) + settings.REFRESH_TOKEN_TIME,
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

    return tokens


auth_router.include_router(google_router)


@auth_router.post(
    "/refresh", status_code=200, response_model=TokenResponse, tags=["AUTHENTICATION"]
)
async def refresh_tokens(db: DBsession, refresh_token: RefreshToken):

    user_id, session_id, token_id, _ = decode_refresh_token(refresh_token)

    user = await db.scalar(
        select(User).where(User.id == UUID(user_id), User.is_active == True)
    )

    if not user:
        raise HTTPException(404, detail="User not found")

    session = await db.scalar(
        select(UserSession).where(
            UserSession.id == UUID(session_id), UserSession.is_active == True
        )
    )

    if not session:
        raise exc

    if session.active_token_id != UUID(token_id):  # WARNING !!!
        session.is_active = False
        await db.commit()
        raise exc

    new_token_id = uuid7()

    session.expiration_time = datetime.now(timezone.utc) + settings.REFRESH_TOKEN_TIME
    session.active_token_id = new_token_id

    refresh_data = {
        "sub": str(user_id),
        "session_id": str(session_id),
        "token_id": str(new_token_id),
    }

    access_data = {"sub": str(user_id)}

    tokens = create_tokens(access_data, refresh_data)

    await db.commit()

    return tokens


@auth_router.delete("/logout", status_code=204, tags=["AUTHENTICATION"])
async def delete_user_session(db: DBsession, refresh_token: RefreshToken):
    _, session_id, *_ = decode_refresh_token(refresh_token)
    session = await db.scalar(
        select(UserSession).where(
            UserSession.id == UUID(session_id), UserSession.is_active == True
        )
    )

    if not session:
        raise exc

    session.is_active = False

    await db.commit()
