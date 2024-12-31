"""Module for the /zones routes"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request, status

from api.db.repository_zone import ZoneTypeRepository as ZoneTypeRepoClass
from api.dependencies.repository_factory import get_repository
from api.models import db_models
from api.models.models import (
    JsonApiLinks,
    JsonApiResponse,
)
from api.models.zone_models import (
    ZoneTypeCreate,
    ZoneTypeResource,
    ZoneTypeUpdate,
)

router = APIRouter(
    prefix="/v1/zones",
    tags=["zones"],
    responses={404: {"description": "Not found"}},
)

ZoneTypeRepository = Annotated[
    ZoneTypeRepoClass,
    Depends(get_repository(db_models.ZoneType, repository_class=ZoneTypeRepoClass)),
]


@router.get("/types", response_model=JsonApiResponse[ZoneTypeResource])
async def get_zone_types(
    request: Request, zone_type_repository: ZoneTypeRepository
) -> JsonApiResponse[ZoneTypeResource]:
    """Get all zone types"""
    zone_types = await zone_type_repository.get_zone_types()

    base_url = str(request.base_url).rstrip("/")
    collection_url = f"{base_url}/v1/zones/types"

    return JsonApiResponse(
        data=[
            ZoneTypeResource.from_db_model(zone_type, collection_url) for zone_type in zone_types
        ],
        links=JsonApiLinks(self_link=collection_url),
    )


@router.post(
    "/types", response_model=JsonApiResponse[ZoneTypeResource], status_code=status.HTTP_201_CREATED
)
async def create_zone_type(
    zone_type_repository: ZoneTypeRepository, request: Request, zone_type_data: ZoneTypeCreate
) -> JsonApiResponse[ZoneTypeResource]:
    """Create a new zone type"""
    zone_type_data_dict = zone_type_data.model_dump()
    zone_type = await zone_type_repository.create_zone_type(zone_type_data_dict)

    base_url = str(request.base_url).rstrip("/")
    resource_url = f"{base_url}/v1/zones/types/{zone_type.id}"

    return JsonApiResponse(
        data=ZoneTypeResource.from_db_model(zone_type, resource_url),
        links=JsonApiLinks(self_link=resource_url),
    )


@router.patch("/types/{zone_type_id}", response_model=JsonApiResponse[ZoneTypeResource])
async def update_zone_type(
    zone_type_repository: ZoneTypeRepository,
    request: Request,
    zone_type_data: ZoneTypeUpdate,
    zone_type_id: int = Path(..., ge=1),
) -> JsonApiResponse[ZoneTypeResource]:
    """Update a zone type by ID"""
    zone_type_data_dict = zone_type_data.model_dump(exclude_unset=True)
    zone_type = await zone_type_repository.update_zone_type(zone_type_id, zone_type_data_dict)

    base_url = str(request.base_url).rstrip("/")
    resource_url = f"{base_url}/v1/zones/types/{zone_type_id}"

    return JsonApiResponse(
        data=ZoneTypeResource.from_db_model(zone_type, resource_url),
        links=JsonApiLinks(self_link=resource_url),
    )
