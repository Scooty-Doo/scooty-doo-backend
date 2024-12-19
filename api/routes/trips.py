"""Module for the /trips routes"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from api.db.repository_trip import TripRepository as TripRepoClass
from api.dependencies.repository_factory import get_repository
from api.models import db_models
from api.models.models import (
    JsonApiError,
    JsonApiErrorResponse,
    JsonApiLinks,
    JsonApiResponse,
)

from api.models.trip_models import TripResource, TripCreate, UserTripStart

router = APIRouter(
    prefix="/v1/trips",
    tags=["trips"],
    responses={404: {"description": "Not found"}},
)

TripRepository = Annotated[
    TripRepoClass,
    Depends(get_repository(db_models.Trip, repository_class=TripRepoClass)),
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
    trip_data: UserTripStart,
    trip_repository: TripRepository
) -> JsonApiResponse[TripResource]:
    """Endpoint for user to start a trip"""
    
    # Check if user is allowed to rent
    
    # Check if bike is available
    return 