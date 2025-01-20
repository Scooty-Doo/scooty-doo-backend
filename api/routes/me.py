"""Module for the /users routes"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Security, status

from api.db.repository_transaction import TransactionRepository as TransactionRepoClass
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
from api.models.transaction_models import TransactionResourceMinimal
from api.models.trip_models import (
    TripResource,
)
from api.models.user_models import UserResource, UserUpdate
from api.services.oauth import security_check

router = APIRouter(
    prefix="/v1/me",
    tags=["me"],
    responses={404: {"description": "Not found"}},
)

UserRepository = Annotated[
    UserRepoClass,
    Depends(get_repository(db_models.User, repository_class=UserRepoClass)),
]

TripRepository = Annotated[
    TripRepoClass,
    Depends(get_repository(db_models.Trip, repository_class=TripRepoClass)),
]

TransactionRepository = Annotated[
    TransactionRepoClass,
    Depends(get_repository(db_models.Transaction, repository_class=TransactionRepoClass)),
]


def raise_forbidden(detail: str):
    """Raise a 403 error in JSON:API format.
    TODO: Change to work the same way as validation error? Move to exceptions?"""
    raise HTTPException(
        status_code=403,
        detail=JsonApiErrorResponse(
            errors=[JsonApiError(status="404", title="Forbidden", detail=detail)]
        ).model_dump(),
    )


@router.get("/", response_model=JsonApiResponse[UserResource])
async def get_my_user(
    user_id: Annotated[int, Security(security_check, scopes=["user"])],
    user_repository: UserRepository,
    request: Request,
) -> JsonApiResponse[UserResource]:
    """Get a user by ID in token"""
    user = await user_repository.get_user(user_id)

    base_url = str(request.base_url).rstrip("/")
    resource_url = f"{base_url}/v1/me"

    return JsonApiResponse(
        data=UserResource.from_db_model(user, resource_url),
        links=JsonApiLinks(self_link=resource_url),
    )


@router.patch("/", response_model=JsonApiResponse[UserResource])
async def update_my_user(
    user_id: Annotated[int, Security(security_check, scopes=["user"])],
    user_repository: UserRepository,
    user_data: UserUpdate,
    request: Request,
) -> JsonApiResponse[UserResource]:
    """Updates a users own information"""
    user_data_dict = user_data.model_dump(exclude_unset=True)
    user = await user_repository.update_user(user_id, user_data_dict)

    base_url = str(request.base_url).rstrip("/")
    resource_url = f"{base_url}/v1/me"

    return JsonApiResponse(
        data=UserResource.from_db_model(user, resource_url),
        links=JsonApiLinks(self_link=resource_url),
    )


@router.get("/trips", response_model=JsonApiResponse[TripResource])
async def get_my_trips(
    user_id: Annotated[int, Security(security_check, scopes=["user"])],
    trip_repository: TripRepository,
    request: Request,
) -> JsonApiResponse[TripResource]:
    """Get all trips for your user"""
    filter_dict = {"user_id": user_id}
    user = await trip_repository.get_trips(**filter_dict)

    base_url = str(request.base_url).rstrip("/")
    resource_url = f"{base_url}/v1/me/trips"

    return JsonApiResponse(
        data=[TripResource.from_db_model(trip, resource_url) for trip in user],
        links=JsonApiLinks(self_link=resource_url),
    )


@router.get("/trips/{trip_id}", response_model=JsonApiResponse[TripResource])
async def get_trip(
    user_id: Annotated[int, Security(security_check, scopes=["user"])],
    request: Request,
    trip_id: int,
    trip_repository: TripRepository,
) -> JsonApiResponse[TripResource]:
    """Get a single trip by ID."""
    trip = await trip_repository.get_trip(trip_id)
    print(trip)
    if trip.user_id != user_id:
        raise_forbidden("Trip user id doesn't match current user id.")

    base_url = str(request.base_url) + "v1/me/trips/"
    self_url = base_url + str(trip_id)
    return JsonApiResponse(
        data=TripResource.from_db_model(trip, base_url),
        links=JsonApiLinks(self_link=self_url),
    )


@router.get("/transactions", response_model=JsonApiResponse[TransactionResourceMinimal])
async def get_my_user_transactions(
    user_id: Annotated[int, Security(security_check, scopes=["user"])],
    transaction_repository: TransactionRepository,
    request: Request,
) -> JsonApiResponse[TransactionResourceMinimal]:
    """Get all transactions for your user"""
    transactions = await transaction_repository.get_transactions(user_id=user_id)

    base_url = str(request.base_url).rstrip("/")
    resource_url = f"{base_url}/v1/me/transactions"

    return JsonApiResponse(
        data=[
            TransactionResourceMinimal.from_db_model(transaction, resource_url)
            for transaction in transactions
        ],
        links=JsonApiLinks(self_link=resource_url),
    )

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: Annotated[int, Security(security_check, scopes=["user"])],
    user_repository: UserRepository,
) -> None:
    """Delete a user by ID"""
    await user_repository.delete_user(user_id)

    return