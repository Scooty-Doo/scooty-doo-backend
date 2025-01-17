"""Module for testing trip routes"""

from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.security.oauth2 import SecurityScopes
from httpx import ASGITransport, AsyncClient

from api.db.repository_user import UserRepository
from api.main import app
from api.routes.me import security_check
from tests.mock_files.objects import fake_me_data
from tests.utils import get_fake_json_data


class TestMe:
    """Class to test trip functionality"""

    async def mock_security_check(self, _1: str = "", _2: SecurityScopes = None):
        """Mocks security check"""
        return 1201279949800724

    @pytest.mark.asyncio
    async def test_get_me(self, monkeypatch):
        """Tests get trips route"""

        app.dependency_overrides[security_check] = self.mock_security_check

        mock_user = AsyncMock(return_value=fake_me_data)
        monkeypatch.setattr(UserRepository, "get_user", mock_user)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost:8000/"
        ) as ac:
            response = await ac.get("v1/me/")

        assert response.status_code == 200
        assert response.json() == get_fake_json_data("me")
