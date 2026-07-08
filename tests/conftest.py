from app.routes.app import app
from app.database import get_db
from app.models import User, UserSession
from app.services.security import create_tokens
from app.settings import settings
from app.models.enums import UserRole
import pytest
from httpx import ASGITransport, AsyncClient
from uuid6 import uuid7
from datetime import datetime, timezone


# I don't need Base.create_all() or Base.delete_all(), since prestart.sh handles that.
# However, for API testing, we will need ASGITransport and AsyncClient.
# Right now, I'm only writing API tests for this project (because I'm foolish and don't use the API -> REPOSITORY -> SERVICE architecture).
@pytest.fixture(scope="function")
async def db():
    async for session in get_db():
        yield session


@pytest.fixture(scope="function")
async def auth_client(db):
    """An asynchronous generator that returns a CLIENT for API testing and closes it at the end of the function."""
    id = uuid7()
    token_id = uuid7()
    session_id = uuid7()
    access_data = {"sub": f"{id}"}
    refresh_data = {
        "sub": f"{id}",
        "session_id": f"{session_id}",
        "token_id": f"{token_id}",
    }
    access_token = create_tokens(access_data=access_data, refresh_data=refresh_data)[
        "access_token"
    ]

    client = User(
        id=id, google_id=f"{uuid7()}", name="TESTER", email=f"user_{id}@gmail.com"
    )
    session = UserSession(
        id=session_id,
        user_id=id,
        active_token_id=token_id,
        expiration_time=datetime.now(timezone.utc) + settings.REFRESH_TOKEN_TIME,
    )
    db.add(client)
    db.add(session)
    headers = {"Authorization": f"Bearer {access_token}"}
    await db.commit()
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport, base_url="http://test/", headers=headers
    ) as client:
        yield id, client


@pytest.fixture(scope="function")
async def auth_admin(db):
    """An asynchronous generator that returns a ADMIN for API testing and closes it at the end of the function."""
    id = uuid7()
    token_id = uuid7()
    session_id = uuid7()
    access_data = {"sub": f"{id}"}
    refresh_data = {
        "sub": f"{id}",
        "session_id": f"{session_id}",
        "token_id": f"{token_id}",
    }
    access_token = create_tokens(access_data=access_data, refresh_data=refresh_data)[
        "access_token"
    ]

    client = User(
        id=id,
        google_id=f"{uuid7()}",
        name="TESTER",
        email=f"user_{id}@gmail.com",
        role=UserRole.admin,
    )
    session = UserSession(
        id=session_id,
        user_id=id,
        active_token_id=token_id,
        expiration_time=datetime.now(timezone.utc) + settings.REFRESH_TOKEN_TIME,
    )
    db.add(client)
    db.add(session)
    headers = {"Authorization": f"Bearer {access_token}"}
    await db.commit()
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport, base_url="http://test/", headers=headers
    ) as client:
        yield id, client

