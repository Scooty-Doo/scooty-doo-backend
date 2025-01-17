"""Module for the /admins routes"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Security

from api.db.repository_admin import AdminRepository as AdminRepoClass
from api.dependencies.repository_factory import get_repository
from api.models import db_models
from api.models.admin_models import AdminGetRequestParams, AdminResource
from api.models.models import (
    JsonApiLinks,
    JsonApiResponse,
)
from api.services.oauth import security_check

router = APIRouter(
    prefix="/v1/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

AdminRepository = Annotated[
    AdminRepoClass,
    Depends(get_repository(db_models.Admin, repository_class=AdminRepoClass)),
]


@router.get("/", response_model=JsonApiResponse[AdminResource])
async def get_my_admin(
    admin_id: Annotated[int, Security(security_check, scopes=["admin"])],
    admin_repository: AdminRepository,
    request: Request,
) -> JsonApiResponse[AdminResource]:
    """Get a admin by ID in token"""
    admin = await admin_repository.get_admin(admin_id)

    base_url = str(request.base_url).rstrip("/")
    resource_url = f"{base_url}/v1/admin"

    return JsonApiResponse(
        data=AdminResource.from_db_model(admin, resource_url),
        links=JsonApiLinks(self_link=resource_url),
    )


@router.get("/all", response_model=JsonApiResponse[AdminResource])
async def get_admins(
    _: Annotated[int, Security(security_check, scopes=["admin"])],
    admin_repository: AdminRepository,
    query_params: Annotated[AdminGetRequestParams, Query()],
    request: Request,
) -> JsonApiResponse[AdminResource]:
    """Get a admin by ID in token"""
    admin = await admin_repository.get_admins(**query_params.model_dump(exclude_none=True))

    base_url = str(request.base_url).rstrip("/")
    resource_url = f"{base_url}/v1/admin/get_all"

    return JsonApiResponse(
        data=[AdminResource.from_db_model(admin, resource_url) for admin in admin],
        links=JsonApiLinks(self_link=resource_url),
    )
