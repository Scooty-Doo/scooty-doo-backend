"""Module for the /users routes"""

from datetime import datetime
import random
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, Request, status, Path, Body
from api.db.repository_user import UserRepository as UserRepoClass
from api.dependencies.repository_factory import get_repository
from api.models import db_models
from api.models.models import (
    JsonApiLinks,
    JsonApiResponse,
)
from api.models.user_models import (
    UserResource,
    UserCreate,
    UserUpdate,
    UserGetRequestParams,
)

router = APIRouter(
    prefix="/v1/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

UserRepository = Annotated[
    UserRepoClass,
    Depends(get_repository(db_models.User, repository_class=UserRepoClass)),
]


@router.get("/{user_id}", response_model=JsonApiResponse[UserResource])
async def get_user(
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
        links=JsonApiLinks(self=resource_url),
    )

@router.get("/", response_model=JsonApiResponse[UserResource])
async def get_users(
    request: Request,
    user_repository: UserRepository,
    query_params: Annotated[UserGetRequestParams, Query()],
) -> JsonApiResponse[UserResource]:
    """Get users from the db. Defaults to showing first 100 users"""
    users = await user_repository.get_users(**query_params.model_dump(exclude_none=True))
    base_url = str(request.base_url).rstrip("/")
    collection_url = f"{base_url}/v1/users"

    return JsonApiResponse(
        data=[UserResource.from_db_model(user, f"{collection_url}/{user.id}") for user in users],
        links=JsonApiLinks(self=collection_url),
    )

@router.post("/", response_model=JsonApiResponse[UserResource], status_code=status.HTTP_201_CREATED)
async def create_user(
    user_repository: UserRepository,
    request: Request,
    user_data: UserCreate,
) -> JsonApiResponse[UserResource]:
    """Create a new user"""
    user_data_dict = user_data.model_dump()
    user = await user_repository.create_user(user_data_dict)
    
    base_url = str(request.base_url).rstrip("/")
    resource_url = f"{base_url}/v1/users/{user.id}"
    
    return JsonApiResponse(
        data=UserResource.from_db_model(user, resource_url),
        links=JsonApiLinks(self=resource_url),
    )

@router.patch("/{user_id}", response_model=JsonApiResponse[UserResource])
async def update_user(
    user_repository: UserRepository,
    request: Request,
    user_data: UserUpdate,
    user_id: int = Path(..., ge=1),
) -> JsonApiResponse[UserResource]:
    """Update a user by ID"""
    user_data_dict = user_data.model_dump()
    user = await user_repository.update_user(user_id, user_data_dict)
    
    base_url = str(request.base_url).rstrip("/")
    resource_url = f"{base_url}/v1/users/{user_id}"
    
    return JsonApiResponse(
        data=UserResource.from_db_model(user, resource_url),
        links=JsonApiLinks(self=resource_url),
    )