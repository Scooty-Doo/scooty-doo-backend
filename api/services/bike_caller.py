import json
from datetime import datetime, timedelta, timezone

import httpx

from api.config import settings
from api.exceptions import BikeRejectedError, BikeServiceUnavailableError
from api.models.trip_models import (
    BikeTripEndData,
    BikeTripEndRequest,
    BikeTripStartData,
    BikeTripStartRequest,
)

EXAMPLE_BASE_URL = "http://localhost:8001"
MOCK_DATA = {
    "message": "Trip ended successfully",
    "data": {
        "report": {
            "city_id": 1,
            "last_position": "POINT(13.10005 55.55034)",
            "battery_lvl": 85.5,
            "is_available": True,
        },
        "log": {
            "user_id": 652134919185249719,
            "bike_id": "1",
            "trip_id": 123,
            "start_time": "2024-12-23T13:22:28.506298+00:00",
            "end_time": "2024-12-23T13:22:36.545233+00:00",
            "start_position": "POINT(13.06782 55.577859)",
            "end_position": "POINT(13.100047 55.55034)",
            "path_taken": "LINESTRING(13.06782 55.57786,13.06787 55.57785,13.07128 55.57756,"
            "13.0713 55.57767,13.07141 55.57799,13.07145 55.5781,13.07162 55.5788,13.07188 55.57876"
            ",13.07307 55.57858,13.07436 55.57839,13.07524 55.57822,13.07659 55.57793,"
            "13.07708 55.57779,13.07726 55.57772,13.07759 55.5776,13.07783 55.5775,"
            "13.07807 55.57739,13.07829 55.57727,13.07884 55.57697,13.07928 55.57672,"
            "13.07956 55.57657,13.07983 55.57645,13.08014 55.57631,13.08054 55.57616,"
            "13.08093 55.57604,13.08133 55.57592,13.08178 55.57582,13.08226 55.57573,"
            "13.08341 55.57556,13.08405 55.57547,13.08464 55.57538,13.08505 55.57531,"
            "13.08534 55.57525,13.08561 55.57518,13.08585 55.57511,13.08618 55.57498,"
            "13.08658 55.57481,13.08648 55.5747,13.08639 55.5746,13.08634 55.57454,"
            "13.08633 55.5745,13.0863 55.57438,13.08616 55.57374,13.08596 55.57291,"
            "13.08572 55.57194,13.08553 55.5711,13.08529 55.5701,13.08511 55.56931,"
            "13.08498 55.5686,13.08496 55.56838,13.08494 55.56819,13.08495 55.56792,"
            "13.08496 55.5676,13.085 55.56729,13.08506 55.56692,13.08507 55.56686,"
            "13.08512 55.56671,13.08533 55.5662,13.08546 55.56597,13.08579 55.56546,"
            "13.0862 55.56495,13.0865 55.56462,13.08684 55.56429,13.08706 55.5641,"
            "13.08724 55.56397,13.08744 55.56385,13.08761 55.56376,13.08784 55.56365,"
            "13.08804 55.56356,13.0883 55.56346,13.08866 55.56334,13.08942 55.56316,"
            "13.08978 55.56311,13.09019 55.56306,13.09093 55.56297,13.09137 55.56291,"
            "13.09144 55.56289,13.09174 55.56283,13.09211 55.56275,13.09245 55.56266,"
            "13.093 55.56247,13.09338 55.56232,13.0938 55.56215,13.09438 55.56191,13.09521 55.56159"
            ",13.09631 55.56112,13.09829 55.56032,13.1001 55.55957,13.10176 55.55889,"
            "13.10303 55.55839,13.10355 55.55817,13.10397 55.55801,13.10477 55.5577,"
            "13.10425 55.5573,13.10324 55.55662,13.10312 55.55653,13.10229 55.55601,"
            "13.10138 55.55549,13.10062 55.55506,13.10033 55.55491,13.09983 55.55467,"
            "13.09929 55.55442,13.09819 55.55391,13.09782 55.55375,13.09775 55.55372,"
            "13.09787 55.55361,13.09829 55.55329,13.09884 55.55279,13.09917 55.55252,"
            "13.09889 55.55239,13.09857 55.55231,13.098 55.55229,13.09764 55.55233,"
            "13.09762 55.55229,13.09745 55.55193,13.0974 55.55183,13.09818 55.55142,"
            "13.09875 55.55103,13.09915 55.55074,13.09935 55.5506,13.09972 55.55037,"
            "13.09997 55.55027,13.10005 55.55034)",
        },
    },
}


async def mock_start_trip(bike_id: int, user_id: int, trip_id: int) -> BikeTripStartData:
    """Mock bike service start trip."""
    mock_data_only = MOCK_DATA["data"]
    start_time = datetime.now(timezone.utc)
    end_time = start_time + timedelta(minutes=30)
    mock_data_only["log"]["start_time"] = start_time.isoformat()
    mock_data_only["log"]["end_time"] = end_time.isoformat()
    mock_data_only["log"]["trip_id"] = trip_id
    mock_data_only["log"]["user_id"] = user_id
    return BikeTripStartData(**mock_data_only)


async def mock_end_trip(
    bike_id: int, user_id: int, trip_id: int, maintenance: bool = False, ignore_zone: bool = False
) -> BikeTripEndData:
    """Mock bike service end trip."""
    mock_data_only = MOCK_DATA["data"]
    start_time = datetime.now(timezone.utc)
    end_time = start_time + timedelta(minutes=30)
    mock_data_only["log"]["start_time"] = start_time.isoformat()
    mock_data_only["log"]["end_time"] = end_time.isoformat()
    mock_data_only["log"]["trip_id"] = trip_id
    mock_data_only["log"]["user_id"] = user_id
    return BikeTripEndData(**mock_data_only)


async def start_trip(bike_id: int, user_id: int, trip_id: int) -> BikeTripStartData:
    """Call bike service to start trip."""
    async with httpx.AsyncClient() as client:
        try:
            request_data = BikeTripStartRequest(
                user_id=user_id,
                trip_id=trip_id,
            ).model_dump()
            response = await client.post(
                f"{EXAMPLE_BASE_URL}/start_trip?bike_id={bike_id}",
                json=request_data,
                timeout=30,
            )

            if response.content:
                try:
                    json_content = response.json()
                    print("\nResponse JSON:", json.dumps(json_content, indent=4))
                except json.JSONDecodeError as e:
                    print("\nRaw Response Content:", response.text)
                    print("JSON Parse Error:", str(e))
            else:
                print("\nEmpty Response Content")

            trip_data = json_content.get("data")
            return BikeTripStartData(**trip_data)

        except httpx.HTTPStatusError as exc:
            error_detail = exc.response.json().get("detail", str(exc))
            raise BikeRejectedError(error_detail) from exc
        except httpx.RequestError as exc:
            raise BikeServiceUnavailableError(
                f"Could not connect to bike service: {str(exc)}"
            ) from exc
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise


async def end_trip(
    bike_id: int, user_id: int, trip_id: int, maintenance: bool = False, ignore_zone: bool = False
) -> BikeTripEndData:
    """Call bike service to end trip."""
    async with httpx.AsyncClient() as client:
        try:
            request_data = BikeTripEndRequest(
                user_id=user_id, trip_id=trip_id, maintenance=maintenance, ignore_zone=ignore_zone
            ).model_dump()

            print("\n=== Request Data ===")
            print(json.dumps(request_data, indent=2))

            response = await client.post(
                f"{EXAMPLE_BASE_URL}/end_trip?bike_id={bike_id}",
                json=request_data,
                timeout=30,
            )

            print("\n=== Response Details ===")
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")

            try:
                json_content = response.json()
                print("\n=== Response JSON ===")
                print(json.dumps(json_content, indent=2))
                trip_data = json_content.get("data")
                return BikeTripEndData(**trip_data)
            except json.JSONDecodeError as e:
                print(f"\nFailed to decode JSON: {e}")
                print(f"Raw content: {response.text}")
                raise BikeServiceUnavailableError("Failed to decode response") from e

        except httpx.HTTPStatusError as exc:
            error_detail = exc.response.json().get("detail", str(exc))
            raise BikeRejectedError(error_detail) from exc
        except httpx.RequestError as exc:
            raise BikeServiceUnavailableError(
                f"Could not connect to bike service: {str(exc)}"
            ) from exc
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise BikeServiceUnavailableError("Unexpected error during bike service call") from e


# Dependency injection
def get_bike_service():
    if settings.use_mocked_bike_call:
        return mock_start_trip, mock_end_trip
    return start_trip, end_trip
