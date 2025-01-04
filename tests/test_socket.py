"""Module for testing bike module"""

import copy
import json
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from api.db.repository_bike import BikeRepository
from api.main import app
from api.socket.socket import socket
from tests.mock_files.objects import fake_bike_data


class TestSocket:
    """Class to test socket functionality"""

    fake_input_data = {
        "battery_lvl": 43,
        "city_id": 1,
        "last_position": "POINT(11.9746 57.7089)",
        "is_available": "true",
        "meta_data": None,
    }

    fake_socket_data = {
        "bike_id": 1,
        "last_position": "POINT(11.9746 57.7089)",
        "city_id": 1,
        "battery_lvl": 43,
        "is_available": "true",
        "meta_data": None,
    }

    @pytest.mark.asyncio
    async def test_socket_emit(self, monkeypatch):
        """Tests socket emitting"""
        # Mock database call
        mock_get_bike = AsyncMock(return_value=fake_bike_data[0])
        monkeypatch.setattr(BikeRepository, "get", mock_get_bike)
        fake_updated_bike = copy.copy(fake_bike_data[0])
        fake_updated_bike.battery_lvl = 43
        fake_updated_bike.last_position = "POINT(11.9746 57.7089)"
        fake_updated_bike.is_available = "true"
        mock_update_bike = AsyncMock(return_value=fake_updated_bike)
        monkeypatch.setattr(BikeRepository, "update_bike", mock_update_bike)

        # Mock socket emit function
        mock_socket_emit = AsyncMock()
        monkeypatch.setattr(socket, "emit", mock_socket_emit)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost:8000/"
        ) as ac:
            response = await ac.patch(
                f"v1/bikes/{self.fake_socket_data['bike_id']}",
                content=json.dumps(self.fake_input_data),
            )

        assert response.status_code == 200
        mock_socket_emit.assert_awaited_once_with(
            "bike_update", data=self.fake_socket_data, room="bike_updates"
        )
