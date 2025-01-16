"""Module for the /users routes"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request, Security, status

from api.db.repository_transaction import TransactionRepository as TransactionRepoClass
from api.db.repository_trip import TripRepository as TripRepoClass
from api.db.repository_user import UserRepository as UserRepoClass
from api.dependencies.repository_factory import get_repository
from api.models import db_models
from api.models.models import (
    JsonApiLinks,
    JsonApiResponse,
)
from api.models.transaction_models import (
    TransactionResourceMinimal,
)
from api.models.trip_models import (
    TripResource,
)
from api.models.user_models import (
    UserCreate,
    UserGetRequestParams,
    UserResource,
    UserResourceMinimal,
    UserUpdate,
)
from api.services.oauth import security_check

router = APIRouter(
    prefix="/v1/users",
    tags=["users"],
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


@router.get("/{user_id}", response_model=JsonApiResponse[UserResource])
async def get_user(
    _: Annotated[db_models.User, Security(security_check, scopes=["admin"])],
    user_repository: UserRepository,
    request: Request,
    user_id: int = Path(..., ge=1),
) -> JsonApiResponse[UserResource]:
    """Get a user by ID"""
    user = await user_repository.get_user(user_id)

    base_url = str(request.base_url).rstrip("/")
    resource_url = f"{base_url}/v1/users/{user_id}"

    return JsonApiResponse(
        data=UserResource.from_db_model(user, resource_url),
        links=JsonApiLinks(self_link=resource_url),
    )


@router.get("/", response_model=JsonApiResponse[UserResourceMinimal])
async def get_users(
    _: Annotated[db_models.User, Security(security_check, scopes=["admin"])],
    request: Request,
    user_repository: UserRepository,
    query_params: Annotated[UserGetRequestParams, Query()],
) -> JsonApiResponse[UserResourceMinimal]:
    """Get users from the db. Defaults to showing first 100 users"""
    users = await user_repository.get_users(**query_params.model_dump(exclude_none=True))
    base_url = str(request.base_url).rstrip("/")
    collection_url = f"{base_url}/v1/users"

    return JsonApiResponse(
        data=[
            UserResourceMinimal.from_db_model(user, f"{collection_url}/{user.id}") for user in users
        ],
        links=JsonApiLinks(self_link=collection_url),
    )


@router.post(
    "/", response_model=JsonApiResponse[UserResourceMinimal], status_code=status.HTTP_201_CREATED
)
async def create_user(
    _: Annotated[db_models.User, Security(security_check, scopes=["admin"])],
    user_repository: UserRepository,
    request: Request,
    user_data: UserCreate,
) -> JsonApiResponse[UserResourceMinimal]:
    """Create a new user"""
    user_data_dict = user_data.model_dump()
    user = await user_repository.create_user(user_data_dict)

    base_url = str(request.base_url).rstrip("/")
    resource_url = f"{base_url}/v1/users/{user.id}"

    return JsonApiResponse(
        data=UserResourceMinimal.from_db_model(user, resource_url),
        links=JsonApiLinks(self_link=resource_url),
    )


@router.patch("/{user_id}", response_model=JsonApiResponse[UserResource])
async def update_user(
    _: Annotated[db_models.User, Security(security_check, scopes=["admin"])],
    user_repository: UserRepository,
    request: Request,
    user_data: UserUpdate,
    user_id: int = Path(..., ge=1),
) -> JsonApiResponse[UserResource]:
    """Update a user by ID"""
    user_data_dict = user_data.model_dump(exclude_unset=True)
    user = await user_repository.update_user(user_id, user_data_dict)

    base_url = str(request.base_url).rstrip("/")
    resource_url = f"{base_url}/v1/users/{user_id}"

    return JsonApiResponse(
        data=UserResource.from_db_model(user, resource_url),
        links=JsonApiLinks(self_link=resource_url),
    )


@router.get("/{user_id}/trips", response_model=JsonApiResponse[TripResource])
async def get_user_trips(
    _: Annotated[db_models.User, Security(security_check, scopes=["admin"])],
    trip_repository: TripRepository,
    request: Request,
    user_id: int = Path(..., ge=1),
) -> JsonApiResponse[TripResource]:
    """Get all trips for a user"""
    filter_dict = {"user_id": user_id}
    user = await trip_repository.get_trips(filter_dict)

    base_url = str(request.base_url).rstrip("/")
    resource_url = f"{base_url}/v1/users/{user_id}/trips"

    return JsonApiResponse(
        data=[TripResource.from_db_model(trip, resource_url) for trip in user],
        links=JsonApiLinks(self_link=resource_url),
    )


@router.get("/{user_id}/transactions", response_model=JsonApiResponse[TransactionResourceMinimal])
async def get_user_transactions(
    _: Annotated[db_models.User, Security(security_check, scopes=["admin"])],
    transaction_repository: TransactionRepository,
    request: Request,
    user_id: int = Path(..., ge=1),
) -> JsonApiResponse[TransactionResourceMinimal]:
    """Get all transactions for a user"""
    transactions = await transaction_repository.get_transactions(user_id=user_id)

    base_url = str(request.base_url).rstrip("/")
    resource_url = f"{base_url}/v1/users/{user_id}/transactions"

    return JsonApiResponse(
        data=[
            TransactionResourceMinimal.from_db_model(transaction, resource_url)
            for transaction in transactions
        ],
        links=JsonApiLinks(self_link=resource_url),
    )
