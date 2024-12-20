"""Module for the /trips routes"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from api.db.repository_trip import TripRepository as TripRepoClass
from api.db.repository_user import UserRepository as UserRepoClass
from api.dependencies.repository_factory import get_repository
from api.models import db_models
from api.models.models import (
    JsonApiError,
    JsonApiErrorResponse,
    JsonApiLinks,
    JsonApiResponse,
)

from api.models.trip_models import TripResource, TripCreate, UserTripStart, TripEnd

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
    trip_data: UserTripStart,
    trip_repository: TripRepository,
    user_repository: UserRepository
) -> JsonApiResponse[TripResource]:
    """Endpoint for user to start a trip"""
    # OBS FUNDERA ÖVER VILKA REPOS SOM BEHÖVS OCH HUR DE SKRIVS IN!
    # LADE TILL user_repository: UserRepository VÄLDIGT SNABBT

    #Generellt bör det inte behövas konvertering när geodata matas in i databasen
    # Postgis ska vara inställt för att fixa det på egen hand

    # Indata för det här bör vara userid och bikeid (borde finnas i usertripstart-modellen)

    # 1. Kolla om användaren får hyra. Här ska vi nog på sikt använda oss av metadatafältet
    # Men jag misstänker att det kan strula lite eftersom metadatafält är i binär form
    # SÅ inför test imorgon tänker jag att vi skriver en placeholder för det i user repo,
    # som bara kollar så att användaren användare som har use_prepay=true inte ligger på minus på kontot (balance<=0)

    # 2. Fråga cykeln om den är hyrbar

    # 3. Om 1 och 2 går igenom:
    # triprepo.starttrip() - Tänker jag rätt behövs här behövs förutom userid och bikeid endast startposiotion
    # Jag skapade en separat modell för det i trip_models "TripCreate"
    # Starttid bör automatiskt sättas till tiden raden skapas i databasen
    # Om du ger dig an detta kan jag tycka att du initialt skulle kunna hoppa över bitarna med fees
    # och hårdkoda det på något sätt. Alltså att du matar in det fejkat for now.
    # Så kan jag titta på hur vi bäst löser det med joins/dbfunctioner/triggers/whatever sen

    # Frågan är om vi ska använda response_model=JsonApiResponse[TripResource]
    # Vi kanske istället ska skapa en mer begränsad modell för svaret på en startad tripp
    # Att TripResource har massa fält som först är relevanta efter en avslutad resa
    return 

@router.patch("/", response_model=JsonApiResponse[TripResource], status_code=status.HTTP_200_OK)
async def end_trip(
    request: Request,
    trip_data: TripEnd,
    trip_repository: TripRepository
) -> JsonApiResponse[TripResource]:
    """Endpoint for user to end a trip"""
    # Jag skrev TripEnd-modellen på 5 sekunder och har inte tänkt igenom den

    # 1. Skapa metod för att uppdatera trip i triprepo. 
    # 2. Om du kodar det kan jag tycka att du kan börja med att göra det halvt mockat:
    # - Passa in fees manuellt härifrån
    # - Skit i transaction, men dra av fees från användarens konto
    # Fokusera på hur svarsdatan ska se ut till användaren
    return