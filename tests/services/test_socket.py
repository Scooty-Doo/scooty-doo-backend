"""Module for testing bike module"""

import copy
import json
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.security.oauth2 import SecurityScopes
from httpx import ASGITransport, AsyncClient

from api.db.repository_bike import BikeRepository
from api.db.repository_trip import TripRepository
from api.db.repository_user import UserRepository
from api.main import app
from api.models.trip_models import BikeTripEndData, BikeTripStartData
from api.routes.bikes import security_check
from api.services.socket import socket
from tests.mock_files.objects import fake_bike_data, fake_trip
from tests.utils import get_fake_json_data


class TestSocket:
    """Class to test socket functionality"""

    fake_input_data = {
        "battery_lvl": 43,
        "city_id": 1,
        "last_position": "POINT(11.9746 57.7089)",
        "speed": 13.5,
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

    start_mock_data = get_fake_json_data("bike_caller_start_trip")
    end_mock_data = get_fake_json_data("bike_caller_end_trip")

    async def mock_security_check(token: str = "", security_scopes: SecurityScopes = None):
        return 652134919185249719

    @pytest.mark.asyncio
    async def test_socket_emit_patch(self, monkeypatch):
        """Tests socket emitting"""
        # Mock security check (for all socket tests)
        app.dependency_overrides[security_check] = self.mock_security_check

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
        print(response.json())
        assert response.status_code == 200
        mock_socket_emit.assert_awaited_once_with(
            "bike_update",
            data={
                "battery_lvl": 43,
                "city_id": 1,
                "last_position": "POINT(11.9746 57.7089)",
                "is_available": True,
                "speed": 13.5,
                "meta_data": None,
                "bike_id": 1,
            },
            room="bike_updates",
        )

    @pytest.mark.asyncio
    async def test_socket_emit_start_trip(self, monkeypatch):
        """Tests socket emitting from start_trip"""

        # Setup
        # Mock user eligibility
        mock_check_user = AsyncMock(return_value="")
        monkeypatch.setattr(UserRepository, "check_user_eligibility", mock_check_user)

        # Mock socket emit function
        mock_socket_emit = AsyncMock()
        monkeypatch.setattr(socket, "emit", mock_socket_emit)

        # Mock call to bike
        mock_start_data = AsyncMock(return_value=BikeTripStartData(**self.start_mock_data["data"]))
        monkeypatch.setattr(
            "api.routes.trips.get_bike_service",
            Mock(return_value=(mock_start_data, mock_start_data)),
        )

        # Mock database call
        mock_trip_return = AsyncMock(return_value=fake_trip)
        monkeypatch.setattr(TripRepository, "add_trip", mock_trip_return)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost:8000/"
        ) as ac:
            response = await ac.post(
                "v1/trips/",
                json={"bike_id": 3},
            )

        print(response.json())
        assert response.status_code == 201
        mock_socket_emit.assert_awaited_once_with(
            "bike_update_start",
            data={
                "battery_lvl": 85,
                "city_id": 1,
                "last_position": "POINT(13.10005 55.55034)",
                "speed": 0.0,
                "is_available": False,
                "meta_data": None,
                "bike_id": 1,
                "zone_id": None,
            },
            room="bike_updates",
        )

    @pytest.mark.asyncio
    async def test_socket_emit_end_trip(self, monkeypatch):
        """Tests socket emitting on end trip"""

        # Mock database call
        mock_trip_return = AsyncMock(return_value=fake_trip)
        monkeypatch.setattr(TripRepository, "end_trip", mock_trip_return)

        # Mock socket emit function
        mock_socket_emit = AsyncMock()
        monkeypatch.setattr(socket, "emit", mock_socket_emit)

        # Mock call to bike
        mock_end_data = AsyncMock(return_value=BikeTripEndData(**self.end_mock_data["data"]))
        monkeypatch.setattr(
            "api.routes.trips.get_bike_service", Mock(return_value=(mock_end_data, mock_end_data))
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost:8000/"
        ) as ac:
            response = await ac.patch(
                "v1/trips/12409712904",
                json={"bike_id": 1, "user_id": 652134919185249719},
            )
        print(response.json())

        assert response.status_code == 200
        mock_socket_emit.assert_awaited_once_with(
            "bike_update_end",
            data={
                "battery_lvl": 85,
                "city_id": 1,
                "last_position": "POINT(13.10005 55.55034)",
                "is_available": True,
                "speed": 0.0,
                "meta_data": None,
                "bike_id": 1,
                "zone_id": 3,
            },
            room="bike_updates",
        )
