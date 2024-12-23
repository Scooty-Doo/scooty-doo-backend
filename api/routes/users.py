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

@router.get("/", response_model=JsonApiResponse[UserResource])
async def get_users(
    request: Request,
    user_repository: UserRepository,
    name_search: str | None = Query(None),
    email_search: str | None = Query(None),
    balance_gt: float | None = Query(None),
    balance_lt: float | None = Query(None),
    created_at_gt: datetime | None = Query(None),
    created_at_lt: datetime | None = Query(None),
    updated_at_gt: datetime | None = Query(None),
    updated_at_lt: datetime | None = Query(None),
) -> JsonApiResponse[UserResource]:
    """Get all users from the database."""
    users = await user_repository.get_users_with_relations()
    
    base_url = str(request.base_url).rstrip("/")
    collection_url = f"{base_url}/v1/users"
    
    return JsonApiResponse(
        data=[
            UserResource.from_db_model(user, f"{collection_url}/{user.id}")
            for user in users
        ],
        links=JsonApiLinks(self=collection_url),
    )