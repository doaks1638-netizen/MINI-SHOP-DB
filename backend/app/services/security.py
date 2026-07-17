from pwdlib import PasswordHash
from app.core.settings import settings
from app.routes import exc, expired_exc
from datetime import datetime, timezone
import jwt


password_context = PasswordHash.recommended()


def hash_password(password: str):
    return password_context.hash(password)


def verify_password(password: str, hash_password: str):
    return password_context.verify(hash_password, hash)


def create_tokens(access_data: dict, refresh_data: dict):
    access_token_data = access_data.copy()
    refresh_token_data = refresh_data.copy()

    access_token_data.update(
        {
            "exp": datetime.now(timezone.utc) + settings.JWT_ACCESS_TOKEN_TIME,
            "token_type": "access",
        }
    )
    refresh_token_data.update(
        {
            "exp": datetime.now(timezone.utc) + settings.JWT_REFRESH_TOKEN_TIME,
            "token_type": "refresh",
        }
    )

    return {
        "access_token": jwt.encode(
            access_token_data,
            key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        ),
        "refresh_token": jwt.encode(
            refresh_token_data,
            key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        ),
    }


def decode_refresh_token(refresh_token):
    try:
        payload = jwt.decode(
            refresh_token.token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id = payload.get("sub")
        session_id = payload.get("session_id")
        token_id = payload.get("token_id")
        token_type = payload.get("token_type")

        if not user_id or not session_id or not token_id or token_type != "refresh":
            raise exc

    except jwt.ExpiredSignatureError:
        raise expired_exc

    except jwt.InvalidTokenError:
        raise exc

    return (user_id, session_id, token_id, token_type)
