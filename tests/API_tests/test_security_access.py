from app.models import User
from app.routes.app import app
from fastapi import status
import pytest
from sqlalchemy import select
from httpx import ASGITransport, AsyncClient

class TestForbidden:
    async def test_admin_access(self, auth_client):
        id, auth_client = auth_client
        responce = await auth_client.get("/api/v1/admin/orders/")
        assert responce.status_code == status.HTTP_403_FORBIDDEN


class TestUnauthorized:
    async def test_unauthorized_query(self, unauthorized_client):
        responce = await unauthorized_client.get("/api/v1/users/me")
        assert responce.status_code == status.HTTP_401_UNAUTHORIZED
        responce = await unauthorized_client.get("/api/v1/products/")
        assert responce.status_code == status.HTTP_200_OK
