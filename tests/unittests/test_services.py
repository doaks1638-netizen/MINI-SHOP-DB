from app.services.security import create_tokens, decode_refresh_token
from app.core.settings import settings
import pytest
from unittest.mock import MagicMock
import jwt
from datetime import datetime
from fastapi import HTTPException


class TestJWT:
    def test_correct_JWT_decode(self):
        refresh_data, access_data = (
            {"sub": "8383", "session_id": 3, "token_id": 234},
            dict(),
        )
        rez = create_tokens(access_data, refresh_data)
        refresh_token = MagicMock()
        refresh_token.token = rez["refresh_token"]
        assert len(decode_refresh_token(refresh_token)) == 4

    def test_incorrect_JWT_decode(self):
        refresh_data, access_data = (
            {"sub": "8383", "session_id": 3.3, "token_id": 2.434},
            dict(),
        )
        rez = create_tokens(access_data, refresh_data)
        payload = jwt.decode(
            rez["refresh_token"],
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        payload["exp"] = datetime(1, 1, 1)
        token = jwt.encode(
            payload, key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        refresh_token = MagicMock()
        refresh_token.token = token
        with pytest.raises(HTTPException) as exc_info:
            assert len(decode_refresh_token(refresh_token)) == 4
        assert exc_info.value.status_code == 401
