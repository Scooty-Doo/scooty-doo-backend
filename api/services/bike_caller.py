import httpx
from fastapi import HTTPException
from api.models.trip_models import BikeTripEndRequest, BikeTripStartRequest,BikeTripEndData, BikeTripStartData

EXAMPLE_BASE_URL = "localhost:8001"
MOCK_DATA = {
    "message": "Trip ended successfully",
    "data": {
        "report": {
            "id": "77",
            "city_id": 1,
            "last_position": "POINT(13.10005 55.55034)",
            "battery_lvl": 85.5,
            "is_available": True
        },
        "log": {
            "id": "1",
            "user_id": 652134919185249773,
            "start_position": "POINT(13.06782 55.577859)",
            "end_position": "POINT(13.100047 55.55034)",
            "path_taken": "LINESTRING(13.06782 55.57786,...)",
            "start_time": "2024-02-17T04:35:18.719376Z",
            "end_time": "2024-02-17T04:38:56.519376Z"
        }
    }
}

async def mock_start_trip(bike_id: int, user_id: int, trip_id: int) -> BikeTripStartData:
    """Mock bike service start trip."""
    return BikeTripStartData(**MOCK_DATA)

async def mock_end_trip(bike_id: int, maintenance: bool = False, ignore_zone: bool = False) -> BikeTripEndData:
    """Mock bike service end trip."""
    return BikeTripEndData(**MOCK_DATA)

async def start_trip(bike_id: int, user_id: int, trip_id: int) -> BikeTripStartRequest:
    """Call bike service to start trip."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{EXAMPLE_BASE_URL}/start_trip",
            json=BikeTripStartRequest(
                user_id=user_id,
                trip_id=trip_id,
            ).model_dump(),
            timeout=30,
        )
        response.raise_for_status()
        return BikeTripStartData(**response.json())

async def end_trip(bike_id: int, maintenance: bool = False, ignore_zone: bool = False) -> BikeTripEndRequest:
    """Call bike service to end trip."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{EXAMPLE_BASE_URL}/end_trip",
            json=BikeTripEndRequest(
                maintenance=maintenance,
                ignore_zone=ignore_zone
            ).model_dump(),
            timeout=30,
        )
        response.raise_for_status()
        return BikeTripEndData(**response.json())
