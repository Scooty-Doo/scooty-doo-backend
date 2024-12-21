"""Module for the /trips routes"""

from typing import Annotated
import random
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
import httpx
from api.db.repository_bike import BikeRepository as BikeRepoClass
from api.db.repository_trip import TripRepository as TripRepoClass
from api.db.repository_user import UserRepository as UserRepoClass
from api.dependencies.repository_factory import get_repository
from api.exceptions import UserNotEligibleException, UserNotFoundException, ActiveTripExistsException
from api.models import db_models
from api.services.bike_caller import mock_start_trip as bike_start_trip, mock_end_trip as bike_end_trip
from api.models.models import (
    JsonApiError,
    JsonApiErrorResponse,
    JsonApiLinks,
    JsonApiResponse,
)
from api.models.trip_models import TripEnd, TripResource, UserTripStart, BikeTripReport, TripCreate, UserTripEnd
router = APIRouter(
    prefix="/v1/trips",
    tags=["trips"],
    responses={404: {"description": "Not found"}},
)

TripRepository = Annotated[
    TripRepoClass,
    Depends(get_repository(db_models.Trip, repository_class=TripRepoClass)),
]

# FIXME: OBS DENNA SKREV JAG SNABBT IN OCH INTE GENOMTÄNKT
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
    trip_repository : TripRepository,
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
    request: Request,
    trip_id: int,
    trip_repository: TripRepository
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
    bike_repository: BikeRepository
) -> JsonApiResponse[TripResource]:
    """Endpoint for user to start a trip"""
    await user_repository.check_user_eligibility(trip.user_id)
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
        links=JsonApiLinks(self=self_link),
    )

@router.patch("/end", response_model=JsonApiResponse[TripResource], status_code=status.HTTP_200_OK)
async def end_trip(
    request: Request,
    user_trip_data: UserTripEnd,
    trip_repository: TripRepository
) -> JsonApiResponse[TripResource]:
    """Endpoint for user to end a trip"""
    bike_id = user_trip_data.bike_id
    user_id = user_trip_data.user_id
    # TripEND innehåller bara user_id och bike_id
    bike_response = await bike_end_trip(bike_id, False, True)

    return

@router.patch("/", response_model=JsonApiResponse[TripResource], status_code=status.HTTP_200_OK)
async def end_trip(
    request: Request,
    trip_report: BikeTripReport,
    trip_repository: TripRepository
) -> JsonApiResponse[TripResource]:
    """Endpoint for user to end a trip"""

    return

