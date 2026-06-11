# auntification function for future
from fastapi import Depends, Query, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from typing import Annotated
from app.database import DBsession
from app.models.user import User
from app.settings import settings
import jwt

page_number = Annotated[int, Query(gt=0)]


oauth_scheme = OAuth2PasswordBearer("/api/v1/auth/token")

exc = HTTPException(
    401,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

expired_exc = HTTPException(
    401, detail="Token has expired", headers={"WWW-Authenticate": "Bearer"}
)

role_exc = HTTPException(
    403,
    "Administrative privileges are not available. Access denied.",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user_func(db: DBsession, token=Depends(oauth_scheme)):
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        token_type = payload.get("token_type")

        if not user_id or token_type != "access":
            raise exc
    except jwt.ExpiredSignatureError:
        raise expired_exc
    except jwt.InvalidTokenError:
        raise exc

    user = await db.scalar(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    if not user:
        raise exc

    return user


type get_current_user = Annotated[User, Depends(get_current_user_func)]


async def get_current_admin_func(user: get_current_user):
    if user.role != "admin":
        raise role_exc

    return user


async def get_current_creator_func(user: get_current_user):
    if user.role != "creater":
        raise role_exc

    return user


type get_current_admin = Annotated[User, Depends(get_current_admin_func)]
type get_current_creator = Annotated[User, Depends(get_current_creator_func)]
