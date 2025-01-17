"""Module for testing trip routes"""

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from api.db.repository_user import UserRepository
from api.main import app
from api.routes.me import security_check
from tests.mock_files.objects import fake_me_data, fake_users_data
from tests.utils import get_fake_json_data


class TestUsers:
    """Class to user route functionality"""

    async def mock_security_check(self, _: str = "", required_scopes: list = None):
        """Mocks security check for user routes"""
        return {"user_id": 1, "scopes": required_scopes}

    @pytest.mark.asyncio
    async def test_get_users(self, monkeypatch):
        """Tests get users route"""

        app.dependency_overrides[security_check] = self.mock_security_check

        mock_user = AsyncMock(return_value=fake_users_data)
        monkeypatch.setattr(UserRepository, "get_users", mock_user)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost:8000/"
        ) as ac:
            response = await ac.get("v1/users/")

        assert response.status_code == 200
        assert response.json() == get_fake_json_data("users")

    @pytest.mark.asyncio
    async def test_get_user(self, monkeypatch):
        """Tests get users route"""

        app.dependency_overrides[security_check] = self.mock_security_check

        mock_user = AsyncMock(return_value=fake_me_data)
        monkeypatch.setattr(UserRepository, "get_user", mock_user)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost:8000/"
        ) as ac:
            response = await ac.get("v1/users/1201279949800724")

        assert response.status_code == 200
        assert response.json() == get_fake_json_data("user")
