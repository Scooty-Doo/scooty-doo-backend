"""Module for testing zone module"""

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from api.db.repository_zone import MapZoneRepository, ZoneTypeRepository
from api.main import app
from tests.mock_files.objects import fake_zone_type_data, fake_zones_data
from tests.utils import get_fake_json_data


class TestZoneRoute:
    """Class to test zone routes"""

    async def mock_security_check(self, _: str = "", required_scopes: list = None):
        """Mocks security check for zone routes"""
        return {"user_id": 1, "scopes": required_scopes}

    @pytest.mark.asyncio
    async def test_get_all_zones(self, monkeypatch):
        """Tests v1/zones/ route"""
        # Mock database call
        mock_get_zones = AsyncMock(return_value=fake_zones_data)
        monkeypatch.setattr(MapZoneRepository, "get_map_zones", mock_get_zones)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost:8000/"
        ) as ac:
            response = await ac.get("v1/zones/")

        assert response.status_code == 200
        expected_response = get_fake_json_data("mapzones")
        assert response.json() == expected_response

    @pytest.mark.asyncio
    async def test_get_all_zone_types(self, monkeypatch):
        """Tests v1/zones/types route"""
        # Mock database call
        mock_get_zone_types = AsyncMock(return_value=fake_zone_type_data)
        monkeypatch.setattr(ZoneTypeRepository, "get_zone_types", mock_get_zone_types)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost:8000/"
        ) as ac:
            response = await ac.get("v1/zones/types")
        expected_response = get_fake_json_data("zonetypes")
        assert response.json() == expected_response

        assert response.status_code == 200
        expected_response = get_fake_json_data("zonetypes")
        assert response.json() == expected_response
