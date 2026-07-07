import pytest
from httpx import ASGITransport, AsyncClient
from app.routes.app import app
# I don't need Base.create_all() or Base.delete_all(), since prestart.sh handles that.
# However, for API testing, we will need ASGITransport and AsyncClient.
# Right now, I'm only writing API tests for this project (because I'm foolish and don't use the API -> REPOSITORY -> SERVICE architecture).


@pytest.fixture(scope="session")
async def async_client():
    """An asynchronous generator that returns a client for API testing and closes it at the end of the session."""
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test/") as client:
        yield client


