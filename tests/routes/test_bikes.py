"""Module for testing bike module"""

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from api.db.repository_bike import BikeRepository
from api.main import app
from api.routes.bikes import security_check
from tests.mock_files.objects import fake_bike_data
from tests.utils import get_fake_json_data


class TestBikeRoute:
    """Class to test bike routes"""

    async def mock_security_check(self, _: str = "", required_scopes: list = None):
        """Mocks security check for bike routes"""
        return {"user_id": 1, "scopes": required_scopes}

    @pytest.mark.asyncio
    async def test_get_all_bikes(self, monkeypatch):
        """Tests v1/bikes/ route"""
        app.dependency_overrides[security_check] = self.mock_security_check
        # Mock security check
        mocked_check = AsyncMock(return_value=1)
        monkeypatch.setattr("api.routes.bikes.security_check", mocked_check)
        # Mock database call
        mock_get_bikes = AsyncMock(return_value=fake_bike_data)
        monkeypatch.setattr(BikeRepository, "get_bikes", mock_get_bikes)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost:8000/"
        ) as ac:
            response = await ac.get("v1/bikes/")

        assert response.status_code == 200
        expected_response = get_fake_json_data("bikes")
        assert response.json() == expected_response

    @pytest.mark.asyncio
    async def test_get_all_bikes_filter(self, monkeypatch):
        """Tests that the filter parameters are used in db call"""
        # Mocks database call
        mock_get_bikes = AsyncMock(return_value=fake_bike_data)
        monkeypatch.setattr(BikeRepository, "get_bikes", mock_get_bikes)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost:8000/"
        ) as ac:
            response = await ac.get("v1/bikes/?city_id=1&min_battery=10&max_battery=40")

        assert response.status_code == 200

        mock_get_bikes.assert_called_with(
            limit=300,
            offset=0,
            order_by="created_at",
            order_direction="desc",
            city_id=1,
            min_battery=10.0,
            max_battery=40.0,
        )

    @pytest.mark.asyncio
    async def test_get_bike(self, monkeypatch):
        """Tests v1/bikes/{bike_id} route"""

        # Mock database call
        mock_get_bike = AsyncMock(return_value=fake_bike_data[0])
        monkeypatch.setattr(BikeRepository, "get_bike", mock_get_bike)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost:8000/"
        ) as ac:
            response = await ac.get("v1/bikes/1")

        assert response.status_code == 200
        expected_response = get_fake_json_data("bike")
        assert response.json() == expected_response
