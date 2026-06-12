from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.database import DBsession
from app.routes import (
    exc,
)
from app.schemas import (
    UserCreate,
    TokenResponse,
    RefreshToken,
)
from app.models.user import User
from app.models.session import UserSession
from app.services import (
    create_hash_password,
    create_tokens,
    verify_password,
    decode_refresh_token,
    check_session_limit,
)
from sqlalchemy import select
from uuid import UUID
from uuid6 import uuid7
from datetime import datetime, timezone
from app.settings import settings
from typing import Annotated

auth_router = APIRouter(prefix="/auth", tags=["AUTHENTICATION"])


@auth_router.post(
    "/registry", status_code=201, response_model=TokenResponse, tags=["AUTHENTICATION"]
)
async def registry_new_user(db: DBsession, new_user: UserCreate):
    same_user = select(User).where(User.email == new_user.email)
    if await db.scalar(same_user):
        raise HTTPException(400, detail="User already exists")
    new_user = User(
        name=new_user.name,
        email=new_user.email,
        hash_password=create_hash_password(new_user.password),
    )
    db.add(new_user)
    await db.flush()

    token_id = uuid7()

    new_session = UserSession(
        user_id=new_user.id,
        active_token_id=token_id,
        expiration_time=datetime.now(timezone.utc) + settings.REFRESH_TOKEN_TIME,
    )
    db.add(new_session)
    await db.flush()

    refresh_data = {
        "sub": str(new_user.id),
        "session_id": str(new_session.id),
        "token_id": str(token_id),
    }

    access_data = {"sub": str(new_user.id)}

    tokens = create_tokens(access_data, refresh_data)

    await db.commit()

    return tokens


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


@auth_router.post(
    "/token", status_code=201, response_model=TokenResponse, tags=["AUTHENTICATION"]
)
async def login(
    db: DBsession, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):

    user = await db.scalar(
        select(User).where(User.email == form_data.username, User.is_active == True)
    )

    credentials_exc = HTTPException(403, detail="Invalid credentials")

    if not user:
        raise credentials_exc

    if not verify_password(form_data.password, user.hash_password):
        raise credentials_exc

    await check_session_limit(db=db, user_id=user.id)

    new_token_id = uuid7()
    session = UserSession(
        user_id=user.id,
        active_token_id=new_token_id,
        expiration_time=datetime.now(timezone.utc) + settings.REFRESH_TOKEN_TIME,
    )
    db.add(session)
    await db.flush()

    refresh_data = {
        "sub": str(user.id),
        "session_id": str(session.id),
        "token_id": str(new_token_id),
    }

    access_data = {"sub": str(user.id)}

    tokens = create_tokens(access_data, refresh_data)

    await db.commit()

    return tokens


@auth_router.delete("/logout", status_code=204, tags=["AUTHENTICATION"])
async def delete_user_session(db: DBsession, refresh_token: RefreshToken):
    user_id, session_id, *_ = decode_refresh_token(refresh_token)
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

    session.is_active = False

    await db.commit()
