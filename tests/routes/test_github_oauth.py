"""Module for testing github oauth"""

from unittest.mock import AsyncMock

import jwt
import pytest
from httpx import ASGITransport, AsyncClient

from api.config import settings
from api.db.repository_user import UserRepository
from api.main import app
from tests.mock_files.objects import fake_user_data


class TestOauthRoutes:
    """Class to test github oauth routes"""

    @pytest.mark.asyncio
    async def test_github_oauth(self, monkeypatch):
        """Tests v1/oauth/github route"""

        # Mock github token call
        mock_access_token = AsyncMock(return_value="awoidhaw90")
        monkeypatch.setattr("api.routes.oauth.get_github_access_token", mock_access_token)
        # Mock github user call
        mock_github_user = AsyncMock(return_value={"login": "HasseBron"})
        monkeypatch.setattr("api.routes.oauth.get_github_user", mock_github_user)

        # Mock database call
        mock_get_user = AsyncMock(return_value=652134919185249719)
        monkeypatch.setattr(UserRepository, "get_user_id_from_github_login", mock_get_user)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost:8000/"
        ) as ac:
            response = await ac.post(
                url="v1/oauth/github",
                headers={"content-type": "application/json"},
                json={"code": "890oaihdawopdgh"},
            )

        mock_get_user.assert_called_once()
        assert response.status_code == 200
        response = response.json()
        assert response["access_token"]
        expected_response = jwt.decode(
            response["access_token"], settings.jwt_secret, algorithms=["HS256"]
        )
        assert str(fake_user_data.id) == expected_response["sub"]
