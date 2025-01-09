"""Module for the /trips routes"""

import random
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, Request, status

from api.db.repository_bike import BikeRepository as BikeRepoClass
from api.db.repository_trip import TripRepository as TripRepoClass
from api.db.repository_user import UserRepository as UserRepoClass
from api.dependencies.repository_factory import get_repository
from api.exceptions import (
    UnauthorizedTripAccessException,
)
from api.models import db_models
from api.models.models import (
    JsonApiLinks,
    JsonApiResponse,
)
from api.models.trip_models import (
    TripCreate,
    TripEndRepoParams,
    TripId,
    TripResource,
    UserTripStart,
)
from api.services.bike_caller import get_bike_service

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
    request: Request,
    trip_repository: TripRepository,
    user_id: Annotated[int | None, Query()] = None,
    bike_id: Annotated[int | None, Query()] = None,
) -> JsonApiResponse[TripResource]:
    """Get all trips from the database."""
    filters = {}
    if user_id:
        filters["user_id"] = user_id
    if bike_id:
        filters["bike_id"] = bike_id

    trips = await trip_repository.get_trips(filters)
    base_url = str(request.base_url).rstrip("/") + request.url.path

    return JsonApiResponse(
        data=[TripResource.from_db_model(trip, base_url) for trip in trips],
        links=JsonApiLinks(self_link=base_url.rsplit("/", 1)[0]),
    )


@router.get("/{trip_id}", response_model=JsonApiResponse[TripResource])
async def get_trip(
    request: Request, trip_id: int, trip_repository: TripRepository
) -> JsonApiResponse[TripResource]:
    """Get a single trip by ID."""
    trip = await trip_repository.get_trip(trip_id)

    base_url = str(request.base_url).rstrip("/") + request.url.path

    return JsonApiResponse(
        data=TripResource.from_db_model(trip, base_url),
        links=JsonApiLinks(self_link=base_url),
    )


@router.post("/", response_model=JsonApiResponse[TripResource], status_code=status.HTTP_201_CREATED)
async def start_trip(
    request: Request,
    trip: UserTripStart,
    trip_repository: TripRepository,
    user_repository: UserRepository,
) -> JsonApiResponse[TripResource]:
    """Endpoint for user to start a trip"""
    bike_start_trip, _ = get_bike_service()

    await user_repository.check_user_eligibility(trip.user_id)

    # TODO: Proper SLID generation
    trip_id = random.randint(1, 1000000)

    # Get bike data first
    bike_data = await bike_start_trip(trip.bike_id, trip.user_id, trip_id)

    # Create trip using bike response data
    trip_data = TripCreate(
        id=trip_id,
        user_id=trip.user_id,
        bike_id=trip.bike_id,
        start_position=bike_data.log.start_position,
        start_time=bike_data.log.start_time,
    )

    created_trip = await trip_repository.add_trip(trip_data)

    base_url = str(request.base_url).rstrip("/")
    self_link = f"{base_url}/v1/trips/{created_trip.id}"
    return JsonApiResponse(
        data=TripResource.from_db_model(created_trip, self_link),
        links=JsonApiLinks(self_link=self_link),
    )


@router.patch("/{trip_id}", response_model=JsonApiResponse[TripResource])
async def end_trip(
    request: Request,
    trip_repository: TripRepository,
    user_trip_data: UserTripStart = Body(..., description="User trip data"),  # noqa: B008
    trip_id: TripId = Path(..., description="ID of the trip to end"),  # noqa: B008
) -> JsonApiResponse[TripResource]:
    """Endpoint for user to end a trip
    TODO: Return link to user and user's transaction?"""
    print(type(trip_id))
    _, bike_end_trip = get_bike_service()
    bike_response = await bike_end_trip(
        user_trip_data.bike_id, user_trip_data.user_id, trip_id, False, True
    )

    #  validate that user, trip and bike match before calling db
    if bike_response.log.user_id != user_trip_data.user_id:
        raise UnauthorizedTripAccessException(
            detail=(
                f"User {user_trip_data.user_id} "
                f"is not allowed to end trip {bike_response.log.user_id}"
            )
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
        user_id=user_trip_data.user_id,
        bike_id=user_trip_data.bike_id,
    )

    # End trip in repository
    updated_trip = await trip_repository.end_trip(repo_params, bike_response.report.is_available)

    base_url = str(request.base_url).rstrip("/")
    self_link = f"{base_url}/v1/trips/{updated_trip.id}"
    return JsonApiResponse(
        data=TripResource.from_db_model(updated_trip, self_link),
        links=JsonApiLinks(self_link=self_link),
    )
