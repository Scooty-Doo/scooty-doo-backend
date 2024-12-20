"""Module for the /trips routes"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from api.db.repository_bike import BikeRepository as BikeRepoClass
from api.db.repository_trip import TripRepository as TripRepoClass
from api.db.repository_user import UserRepository as UserRepoClass
from api.dependencies.repository_factory import get_repository
from api.exceptions import UserNotEligibleException, UserNotFoundException
from api.models import db_models
from api.models.models import (
    JsonApiError,
    JsonApiErrorResponse,
    JsonApiLinks,
    JsonApiResponse,
)
from api.models.trip_models import TripCreate, TripEnd, TripResource, UserTripStart

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

# Skrivit nedan också, men kanske byta ut response_model till en mindre modell
@router.post("/", response_model=JsonApiResponse[TripResource], status_code=status.HTTP_201_CREATED)
async def start_trip(
    request: Request,
    trip: UserTripStart,
    trip_repository: TripRepository,
    user_repository: UserRepository,
    bike_repository: BikeRepository
) -> JsonApiResponse[TripResource]:
    """Endpoint for user to start a trip"""
    trip_data = trip.model_dump()
    try:
        await user_repository.check_user_eligibility(trip.user_id)
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserNotEligibleException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    
    # Prata med cykeln för att se om den är tillgänglig
    # När detta läggs till behöver inte längre trip repo kontroller last_position

    created_trip = await trip_repository.add_trip(trip_data)

    base_url = str(request.base_url).rstrip("/")
    self_link = f"{base_url}/v1/trips/{created_trip.id}"
    trip_resource = TripResource.from_db_model(created_trip, self_link)

    return JsonApiResponse(
        data=trip_resource,
        links=JsonApiLinks(self=self_link),
    )

# @router.patch("/", response_model=JsonApiResponse[TripResource], status_code=status.HTTP_200_OK)
# async def end_trip(
#     request: Request,
#     trip_data: TripEnd,
#     trip_repository: TripRepository
# ) -> JsonApiResponse[TripResource]:
#     """Endpoint for user to end a trip"""
#     # Jag skrev TripEnd-modellen på 5 sekunder och har inte tänkt igenom den

#     # 1. Skapa metod för att uppdatera trip i triprepo. 
#     # 2. Om du kodar det kan jag tycka att du kan börja med att göra det halvt mockat:
#     # - Passa in fees manuellt härifrån
#     # - Skit i transaction, men dra av fees från användarens konto
#     # Fokusera på hur svarsdatan ska se ut till användaren
#     return