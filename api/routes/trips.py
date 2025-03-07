"""Module for the /trips routes"""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, Request, Security, status
from tsidpy import TSID

from api.db.repository_bike import BikeRepository as BikeRepoClass
from api.db.repository_trip import TripRepository as TripRepoClass
from api.db.repository_user import UserRepository as UserRepoClass
from api.dependencies.repository_factory import get_repository
from api.exceptions import (
    UnauthorizedTripAccessException,
)
from api.models import db_models
from api.models.bike_models import BikeSocketStartEnd
from api.models.models import (
    JsonApiLinks,
    JsonApiResponse,
)
from api.models.trip_models import (
    TripCreate,
    TripEndRepoParams,
    TripGetRequestParams,
    TripId,
    TripResource,
    UserTripStart,
)
from api.services.bike_caller import get_bike_service
from api.services.oauth import security_check
from api.services.socket import emit_update_start_end

router = APIRouter(
    prefix="/v1/trips",
    tags=["trips"],
    responses={404: {"description": "Not found"}},
)

TripRepository = Annotated[
    TripRepoClass,
    Depends(get_repository(db_models.Trip, repository_class=TripRepoClass)),
]

UserRepository = Annotated[
    UserRepoClass,
    Depends(get_repository(db_models.User, repository_class=UserRepoClass)),
]

BikeRepository = Annotated[
    BikeRepoClass,
    Depends(get_repository(db_models.Bike, repository_class=BikeRepoClass)),
]
# TODO: Error handling


@router.get("/", response_model=JsonApiResponse[TripResource])
async def get_trips(
    _: Annotated[int, Security(security_check, scopes=["admin"])],
    request: Request,
    trip_repository: TripRepository,
    query_params: Annotated[TripGetRequestParams, Query()],
) -> JsonApiResponse[TripResource]:
    """Get all trips from the database."""
    trips = await trip_repository.get_trips(**query_params.model_dump(exclude_none=True))
    base_url = str(request.base_url).rstrip("/") + request.url.path

    return JsonApiResponse(
        data=[TripResource.from_db_model(trip, base_url) for trip in trips],
        links=JsonApiLinks(self_link=base_url.rsplit("/", 1)[0]),
    )


@router.get("/{trip_id}", response_model=JsonApiResponse[TripResource])
async def get_trip(
    _: Annotated[int, Security(security_check, scopes=["admin"])],
    request: Request,
    trip_id: int,
    trip_repository: TripRepository,
) -> JsonApiResponse[TripResource]:
    """Get a single trip by ID."""
    trip = await trip_repository.get_trip(trip_id)

    base_url = str(request.base_url).rstrip("/") + request.url.path
    base_url = base_url.rsplit("/", 1)[0] + "/"
    self_link = base_url + str(trip_id)

    return JsonApiResponse(
        data=TripResource.from_db_model(trip, base_url),
        links=JsonApiLinks(self_link=self_link),
    )


@router.post("/", response_model=JsonApiResponse[TripResource], status_code=status.HTTP_201_CREATED)
async def start_trip(
    user_id: Annotated[int, Security(security_check, scopes=["user"])],
    request: Request,
    trip: UserTripStart,
    trip_repository: TripRepository,
    user_repository: UserRepository,
) -> JsonApiResponse[TripResource]:
    """Endpoint for user to start a trip"""

    bike_start_trip, _ = get_bike_service()
    await user_repository.check_user_eligibility(user_id)

    tsid_number = TSID.create().number
    max_safe_integer = 9007199254740991
    trip_id = tsid_number % max_safe_integer

    # Get bike data first
    bike_data = await bike_start_trip(trip.bike_id, user_id, trip_id)
    # Create trip using bike response data
    trip_data = TripCreate(
        id=trip_id,
        user_id=user_id,
        bike_id=trip.bike_id,
        start_position=bike_data.log.start_position,
        start_time=bike_data.log.start_time,
    )

    created_trip = await trip_repository.add_trip(trip_data)

    # Emit bike status to socket
    await emit_update_start_end(
        BikeSocketStartEnd(**bike_data.log.model_dump(), **bike_data.report.model_dump()),
        "bike_update_start",
    )

    base_url = str(request.base_url).rstrip("/")
    base_url = f"{base_url}/v1/trips/"
    self_link = base_url + str(trip_id)

    return JsonApiResponse(
        data=TripResource.from_db_model(created_trip, base_url),
        links=JsonApiLinks(self_link=self_link),
    )


@router.patch("/{trip_id}", response_model=JsonApiResponse[TripResource])
async def end_trip(
    user_id: Annotated[int, Security(security_check, scopes=["user"])],
    request: Request,
    trip_repository: TripRepository,
    user_trip_data: UserTripStart = Body(..., description="User trip data"),  # noqa: B008
    trip_id: TripId = Path(..., description="ID of the trip to end"),  # noqa: B008
) -> JsonApiResponse[TripResource]:
    """Endpoint for user to end a trip
    TODO: Return link to user and user's transaction?"""
    _, bike_end_trip = get_bike_service()
    bike_response = await bike_end_trip(user_trip_data.bike_id, user_id, trip_id, False, True)
    #  validate that user, trip and bike match before calling db
    if bike_response.log.user_id != user_id:
        raise UnauthorizedTripAccessException(
            detail=(f"User {user_id} is not allowed to end trip {bike_response.log.user_id}")
        )

    if bike_response.log.trip_id != trip_id:
        raise UnauthorizedTripAccessException(
            detail=f"Trip {trip_id} does not match bike trip {bike_response.log.trip_id}"
        )

    # Create end trip data from bike response
    repo_params = TripEndRepoParams(
        end_time=bike_response.log.end_time,
        end_position=bike_response.log.end_position,
        path_taken=bike_response.log.path_taken,
        trip_id=trip_id,
        user_id=user_id,
        bike_id=user_trip_data.bike_id,
    )
    # End trip in repository
    updated_trip = await trip_repository.end_trip(repo_params, bike_response.report.is_available)

    # Emit bike status to socket
    await emit_update_start_end(
        BikeSocketStartEnd(**bike_response.report.model_dump(), **bike_response.log.model_dump()),
        "bike_update_end",
    )

    base_url = str(request.base_url).rstrip("/")
    base_url_link = f"{base_url}/v1/trips/"
    self_link = base_url_link + str(trip_id)

    return JsonApiResponse(
        data=TripResource.from_db_model(updated_trip, base_url_link),
        links=JsonApiLinks(self_link=self_link),
    )
