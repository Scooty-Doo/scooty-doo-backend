"""Module for testing bike module"""

import pytest
from unittest.mock import AsyncMock
from api.main import app
from api.db.repository_bike import BikeRepository
from httpx import ASGITransport, AsyncClient
from api.models.db_models import Bike
import datetime

# Use pytest asyncio to test async routes
@pytest.mark.asyncio
async def test_get_all_bikes(monkeypatch):
    fake_bike_data = [
        Bike(id = 1, 
            battery_lvl = 45, 
            city_id = 1, 
            is_available = False, 
            meta_data = None,
            created_at = datetime.datetime(2024, 7, 13, 7, 56, 50, 758246, tzinfo=datetime.timezone.utc),
            updated_at = datetime.datetime(2024, 12, 17, 14, 21, 44, 610901, tzinfo=datetime.timezone.utc)),
        Bike(id = 2, 
            battery_lvl = 95, 
            city_id = 3,
            is_available = True,
            meta_data = None,
            created_at = datetime.datetime(2024, 7, 13, 7, 56, 51, 758246, tzinfo=datetime.timezone.utc),
            updated_at = datetime.datetime(2024, 12, 17, 14, 21, 46, 610901, tzinfo=datetime.timezone.utc))
    ]
    async def mock_get_bikes(self, filters):
        return fake_bike_data

    mock_repo = AsyncMock()
    mock_repo.get_bikes = mock_get_bikes

    monkeypatch.setattr(BikeRepository, "get_bikes", mock_repo.get_bikes)
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost:8000/"
    ) as ac:
        response = await ac.get("v1/bikes/")
    
    assert response.status_code == 200

    expected_response = {
        "data": [
            {
                "id": "1",
                "attributes": {
                    "battery_lvl": 45,
                    'created_at': '2024-07-13T07:56:50.758246Z',
                    'is_available': False,
                    'last_position': None,
                    'updated_at': '2024-12-17T14:21:44.610901Z',
                },
                "links": 
                {
                        "self": "http://localhost:8000/v1/bikes/1"
                },
            'relationships': {
                'city': {
                    'data': {
                        'id': '1',
                        'type': 'cities',
                    },
                },
            },
            'type': 'bikes',
            },
            {
                "id": "2",
                "attributes": {
                        "battery_lvl": 95,
                        'created_at': '2024-07-13T07:56:51.758246Z',
                        'is_available': True,
                        'last_position': None,
                        'updated_at': '2024-12-17T14:21:46.610901Z',
                },
                "links": {"self": "http://localhost:8000/v1/bikes/2"
                },
                'relationships': {
                    'city': {
                    'data': {
                        'id': '3',
                        'type': 'cities',
                    },
                },
            },
            'type': 'bikes',
            },
        ],
        'links': {
            'self': 'http://localhost:8000/v1/bikes',
        },

    }

    assert response.json() == expected_response
