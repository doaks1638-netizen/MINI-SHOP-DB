from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
import asyncio
from app.models import User, UserSession, EmailUrl, EmailCode
from app.db.database import DBsession
from app.routes import (
    exc,
)
from app.schemas import (
    TokenResponse,
    RefreshToken,
    UserCreateEmail,
    UserEmail,
    EmailSchema,
)
from app.services import (
    create_tokens,
    decode_refresh_token,
    hash_password,
    verify_password,
    send_url,
    send_code,
    check_session_limit,
)
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from uuid import UUID, uuid4
from uuid6 import uuid7
from datetime import datetime, timezone
from app.core.settings import settings
from typing import Annotated
from fastapi.responses import RedirectResponse
from fastapi import Query
from app.models.enums import UserStatus
import random
from .google_auth import google_router
from app.core.limiter import limiter

auth_router = APIRouter(prefix="/auth", tags=["AUTHENTICATION"])
auth_router.include_router(google_router)
auth_exc = HTTPException(401, detail="Неверные данные для входа")


@auth_router.post("/registry", status_code=201, tags=["AUTHENTICATION"])
@limiter.limit("25/day")
async def registry(
    request: Request, db: DBsession, user_info: UserCreateEmail, background_tasks: BackgroundTasks
):
    same_user_stmt = select(User).where(User.email == user_info.email)
    same_user = await db.scalar(same_user_stmt)
    if same_user:
        raise HTTPException(409, detail="Пользователь с таким email уже существует!")
    else:
        current_user = User(
            name=user_info.name,
            email=user_info.email,
            status=UserStatus.pending,
            password=(await asyncio.to_thread(hash_password, user_info.password)),
        )
        db.add(current_user)
        await db.flush()

    token_id = uuid4()

    new_callback = EmailUrl(
        user_id=current_user.id,
        expire_at=datetime.now(timezone.utc) + settings.JWT_TOKEN_URL_TIME,
        token=token_id,
    )
    db.add(new_callback)
    await db.flush()
    background_tasks.add_task(
        send_url,
        EmailSchema(email=user_info.email),
        f"{settings.EMAIL_CALLBACK}{token_id}",
    )
    await db.commit()


@auth_router.post("/login", status_code=201, tags=["AUTHENTICATION"])
@limiter.limit("25/day")
async def login(request: Request, db: DBsession, user_info: UserEmail, background_tasks: BackgroundTasks):
    same_user_stmt = select(User).where(User.email == user_info.email)
    same_user = await db.scalar(same_user_stmt)
    if not same_user:
        raise auth_exc
    if (
        not (
            await asyncio.to_thread(
                verify_password, user_info.password, same_user.password
            )
        )
        or same_user.status != UserStatus.active
    ):
        raise auth_exc

    code = str(random.randrange(100000, 1000000))

    new_callback = EmailCode(
        user_id=same_user.id,
        expire_at=datetime.now(timezone.utc) + settings.JWT_TOKEN_CODE_TIME,
        code=code,
    )
    db.add(new_callback)
    await db.flush()
    background_tasks.add_task(
        send_code,
        EmailSchema(email=user_info.email),
        code,
    )
    await db.commit()


@auth_router.get("/url_callback", status_code=200, tags=["AUTHENTICATION"])
async def url_callback(db: DBsession, token: Annotated[str, Query(max_length=36)]):
    stmt = (
        select(EmailUrl)
        .where(EmailUrl.token == token)
        .options(selectinload(EmailUrl.user))
    )
    email_url = await db.scalar(stmt)
    if not email_url:
        raise auth_exc
    if datetime.now(timezone.utc) > email_url.expire_at:
        raise HTTPException(410, detail="Повторите регистрацию заново!")
    user = email_url.user
    await check_session_limit(db=db, user_id=user.id)
    user.status = UserStatus.active
    await db.execute(delete(EmailUrl).where(EmailUrl.user_id == user.id))
    token_id = uuid7()
    new_session = UserSession(
        user_id=user.id,
        active_token_id=token_id,
        expiration_time=datetime.now(timezone.utc) + settings.JWT_REFRESH_TOKEN_TIME,
    )
    db.add(new_session)

    await db.flush()

    refresh_data = {
        "sub": str(user.id),
        "session_id": str(new_session.id),
        "token_id": str(token_id),
    }

    access_data = {"sub": str(user.id)}

    tokens = create_tokens(access_data, refresh_data)

    await db.commit()
    return RedirectResponse(
        f"/callback?access_token={tokens['access_token']}&refresh_token={tokens['refresh_token']}"
    )


@auth_router.get("/code_callback", status_code=200, tags=["AUTHENTICATION"])
async def code_callback(db: DBsession, code: Annotated[str, Query(max_length=6)]):
    stmt = (
        select(EmailCode)
        .where(EmailCode.code == code)
        .options(selectinload(EmailCode.user))
    )
    email_code = await db.scalar(stmt)
    if not email_code:
        raise auth_exc
    if datetime.now(timezone.utc) > email_code.expire_at:
        raise HTTPException(410, detail="Повторите аунтификацию заново!")
    user = email_code.user
    await check_session_limit(db=db, user_id=user.id)
    await db.execute(delete(EmailCode).where(EmailCode.id == email_code.id))
    token_id = uuid7()
    new_session = UserSession(
        user_id=user.id,
        active_token_id=token_id,
        expiration_time=datetime.now(timezone.utc) + settings.JWT_REFRESH_TOKEN_TIME,
    )
    db.add(new_session)

    await db.flush()

    refresh_data = {
        "sub": str(user.id),
        "session_id": str(new_session.id),
        "token_id": str(token_id),
    }

    access_data = {"sub": str(user.id)}

    tokens = create_tokens(access_data, refresh_data)

    await db.commit()
    return RedirectResponse(
        f"/callback?access_token={tokens['access_token']}&refresh_token={tokens['refresh_token']}"
    )


@auth_router.post(
    "/refresh", status_code=200, response_model=TokenResponse, tags=["AUTHENTICATION"]
)
async def refresh_tokens(db: DBsession, refresh_token: RefreshToken):

    user_id, session_id, token_id, _ = decode_refresh_token(refresh_token)

    user = await db.scalar(
        select(User).where(User.id == UUID(user_id), User.status == UserStatus.active)
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

    session.expiration_time = (
        datetime.now(timezone.utc) + settings.JWT_REFRESH_TOKEN_TIME
    )
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
