"""Module for testing trip routes"""

from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.security.oauth2 import SecurityScopes
from httpx import ASGITransport, AsyncClient

from api.db.repository_trip import TripRepository
from api.db.repository_user import UserRepository
from api.main import app
from api.models.trip_models import BikeTripEndData, BikeTripStartData
from api.routes.trips import TSID, security_check
from api.services.socket import socket
from tests.mock_files.objects import fake_trip_start, fake_trips
from tests.utils import get_fake_json_data


class TestTrips:
    """Class to test trip functionality"""

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

    start_mock_data = get_fake_json_data("bike_caller_start_trip")
    end_mock_data = get_fake_json_data("bike_caller_end_trip")

    async def mock_security_check(self, _1: str = "", _2: SecurityScopes = None):
        """Mocks security check"""
        return 652134919185249719

    @pytest.mark.asyncio
    async def test_get_trips(self, monkeypatch):
        """Tests get trips route"""

        app.dependency_overrides[security_check] = self.mock_security_check

        mock_trips_return = AsyncMock(return_value=fake_trips)
        monkeypatch.setattr(TripRepository, "get_trips", mock_trips_return)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost:8000/"
        ) as ac:
            response = await ac.get("v1/trips/")

        assert response.status_code == 200
        assert response.json() == get_fake_json_data("trips")

    @pytest.mark.asyncio
    async def test_start_trip(self, monkeypatch):
        """Tests the start trip route aka the post /trips"""
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
        mock_trip_return = AsyncMock(return_value=fake_trip_start)
        monkeypatch.setattr(TripRepository, "add_trip", mock_trip_return)

        # Mock ID generation
        mock_return_value = Mock()
        mock_return_value.number = 12409712904
        mock_tsid_create = Mock(return_value=mock_return_value)

        monkeypatch.setattr(TSID, "create", mock_tsid_create)

        # Act
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://localhost:8000/"
        ) as ac:
            response = await ac.post(
                "v1/trips/",
                json={"bike_id": 3, "user_id": 1},
            )

        # Assert
        assert response.status_code == 201
        assert response.json() == get_fake_json_data("trip_start")

    @pytest.mark.asyncio
    async def test_end_trip(self, monkeypatch):
        """Tests the end trip function, aka patch trip"""
        # Mock database call
        mock_trip_return = AsyncMock(return_value=fake_trips[0])
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

        assert response.status_code == 200
        assert response.json() == get_fake_json_data("trip")

    @pytest.mark.asyncio
    async def test_end_trip_fail_wrong_user(self, monkeypatch):
        """Tests the end trip function, aka patch trip"""
        # Mock database call
        mock_trip_return = AsyncMock(return_value=fake_trips[0])
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
                "v1/trips/123",
                json={"bike_id": 1, "user_id": 12344},
            )

        assert response.status_code == 403
