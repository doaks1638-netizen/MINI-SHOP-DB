from app.routes.app import app
from app.routes.v1.auth import get_google_sso
from unittest.mock import MagicMock
from uuid6 import uuid7
import fastapi


class TestAuth:
    """Authentication testing class, currently only Google, but in the future I'll add Github, X, and Telegram."""

    async def test_google_auth(self, mocker, unauthorized_client):
        google_user = MagicMock()
        google_user.id = f"{uuid7()}"
        google_user.email = f"email_{uuid7()}"
        google_user.display_name = f"name_{uuid7()}"
        google_user.picture = f"https://picture_{uuid7()}"

        async def mock_get_google_sso():
            class MockSSO:
                async def verify_and_process(self, request):
                    return google_user

            return MockSSO()

        app.dependency_overrides[get_google_sso] = mock_get_google_sso
        responce = await unauthorized_client.get("/api/v1/auth/google/callback")
        assert responce.status_code == 307
        assert "/callback?access_token=" in responce.headers['location']
