"""Module for testing bike module"""

from unittest.mock import patch

import pytest

from api.exceptions import BikeServiceUnavailableError
from api.services.bike_caller import (
    datetime,
    end_trip,
    httpx,
    mock_end_trip,
    mock_start_trip,
    start_trip,
)
from tests.mock_files.objects import fake_mock_end_object, fake_mock_start_object
from tests.utils import get_fake_json_data


class TestBikeCaller:
    """Class to test bike caller functionality"""

    start_mock_data = get_fake_json_data("bike_caller_start_trip")
    end_mock_data = get_fake_json_data("bike_caller_end_trip")

    @pytest.mark.asyncio
    @patch(
        "api.services.bike_caller.httpx.AsyncClient.post",
        return_value=httpx.Response(200, json=start_mock_data),
    )
    async def test_start_trip(self, monkeypatch):
        """Tests start trip call."""
        # Setup mock data
        mock_log = self.start_mock_data["data"]["log"]

        # Act
        result = await start_trip(mock_log["bike_id"], mock_log["user_id"], mock_log["trip_id"])

        # Assert
        assert result is not None
        assert result.log.bike_id == int(mock_log["bike_id"])
        assert result.log.trip_id == mock_log["trip_id"]
        monkeypatch.assert_called_once()
        monkeypatch.assert_called_with(
            "http://localhost:8001/start_trip",
            json={"user_id": mock_log["user_id"], "trip_id": mock_log["trip_id"]},
            params={"bike_id": mock_log["bike_id"]},
            timeout=30,
        )

    @pytest.mark.asyncio
    @patch(
        "api.services.bike_caller.httpx.AsyncClient.post",
        return_value=httpx.Response(200, json=end_mock_data),
    )
    async def test_end_trip(self, monkeypatch):
        """Tests end trip call."""
        # Setup mock data
        mock_log = self.end_mock_data["data"]["log"]

        # Act
        result = await end_trip(mock_log["bike_id"], mock_log["user_id"], mock_log["trip_id"])

        # Assert
        assert result is not None
        assert result.log.bike_id == int(mock_log["bike_id"])
        assert result.log.user_id == mock_log["user_id"]
        assert result.log.trip_id == mock_log["trip_id"]
        monkeypatch.assert_called_once()
        monkeypatch.assert_called_with(
            "http://localhost:8001/end_trip",
            json={"maintenance": False, "ignore_zone": False},
            params={"bike_id": mock_log["bike_id"]},
            timeout=30,
        )

    @pytest.mark.asyncio
    @patch(
        "api.services.bike_caller.httpx.AsyncClient.post",
        side_effect=httpx.RequestError("Internal server error"),
    )
    async def test_start_trip_fail(self, monkeypatch):
        """Tests start trip call."""
        # Setup mock data
        mock_log = self.start_mock_data["data"]["log"]

        # Act
        with pytest.raises(BikeServiceUnavailableError) as error:
            await start_trip(mock_log["bike_id"], mock_log["user_id"], mock_log["trip_id"])

        # Assert
        assert "Could not connect to bike service: Internal server error" in str(error.value)
        monkeypatch.assert_called_once()
        monkeypatch.assert_called_with(
            "http://localhost:8001/start_trip",
            json={"user_id": mock_log["user_id"], "trip_id": mock_log["trip_id"]},
            params={"bike_id": mock_log["bike_id"]},
            timeout=30,
        )

    @pytest.mark.asyncio
    @patch(
        "api.services.bike_caller.httpx.AsyncClient.post",
        side_effect=httpx.RequestError("Internal server error"),
    )
    async def test_end_trip_fail(self, monkeypatch):
        """Tests end trip call."""
        # Setup mock data
        mock_log = self.end_mock_data["data"]["log"]

        # Act, Assert
        with pytest.raises(BikeServiceUnavailableError) as error:
            await end_trip(mock_log["bike_id"], mock_log["user_id"], mock_log["trip_id"])

        assert "Could not connect to bike service: Internal server error" in str(error.value)
        monkeypatch.assert_called_once()
        monkeypatch.assert_called_with(
            "http://localhost:8001/end_trip",
            json={"maintenance": False, "ignore_zone": False},
            params={"bike_id": mock_log["bike_id"]},
            timeout=30,
        )

    @pytest.mark.asyncio
    async def test_mock_start_trip(self, monkeypatch):
        """Tests mocked bike caller start"""
        fixed_now = datetime(2025, 1, 19, 17, 25, 39, 596693)

        class MockDateTime(datetime):
            @classmethod
            def now(cls, tz=None):
                return fixed_now

        monkeypatch.setattr("api.services.bike_caller.datetime", MockDateTime)

        res = await mock_start_trip(12, 125125, 1111)
        assert res == fake_mock_start_object

    @pytest.mark.asyncio
    async def test_mock_end_trip(self, monkeypatch):
        """Tests mocked bike caller end"""
        fixed_now = datetime(2025, 1, 19, 17, 25, 39, 596693)

        class MockDateTime(datetime):
            @classmethod
            def now(cls, tz=None):
                return fixed_now

        monkeypatch.setattr("api.services.bike_caller.datetime", MockDateTime)
        res = await mock_end_trip(12, 125125, 1111)
        assert res == fake_mock_end_object
