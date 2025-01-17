"""Module for the /zones routes"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request, Security, status

from api.db.repository_zone import (
    MapZoneRepository as MapZoneRepoClass,
)
from api.db.repository_zone import (
    ZoneTypeRepository as ZoneTypeRepoClass,
)
from api.dependencies.repository_factory import get_repository
from api.models import db_models
from api.models.models import (
    JsonApiLinks,
    JsonApiResponse,
)
from api.models.wkt_models import WKTPoint
from api.models.zone_models import (
    MapZoneCreate,
    MapZoneGetRequestParams,
    MapZoneResource,
    MapZoneResourceMinimal,
    MapZoneUpdate,
    ZoneTypeCreate,
    ZoneTypeResource,
    ZoneTypeUpdate,
)
from api.services.oauth import security_check

router = APIRouter(
    prefix="/v1/zones",
    tags=["zones"],
    responses={404: {"description": "Not found"}},
)

ZoneTypeRepository = Annotated[
    ZoneTypeRepoClass,
    Depends(get_repository(db_models.ZoneType, repository_class=ZoneTypeRepoClass)),
]

MapZoneRepository = Annotated[
    MapZoneRepoClass,
    Depends(get_repository(db_models.MapZone, repository_class=MapZoneRepoClass)),
]


@router.get("/", response_model=JsonApiResponse[MapZoneResourceMinimal])
async def get_zones(
    request: Request,
    map_zone_repository: MapZoneRepository,
    query_params: Annotated[MapZoneGetRequestParams, Query()],
) -> JsonApiResponse[MapZoneResourceMinimal]:
    """Get zones from the db. Defaults to showing first 100 zones"""
    zones = await map_zone_repository.get_map_zones(**query_params.model_dump(exclude_none=True))
    base_url = str(request.base_url).rstrip("/")
    collection_url = f"{base_url}/v1/zones"

    return JsonApiResponse(
        data=[
            MapZoneResourceMinimal.from_db_model(zone, f"{collection_url}/{zone.id}")
            for zone in zones
        ],
        links=JsonApiLinks(self_link=collection_url),
    )


@router.get("/{zone_id}", response_model=JsonApiResponse[MapZoneResource])
async def get_zone(
    # _: Annotated[db_models.Admin, Security(security_check, scopes=["admin"])],
    map_zone_repository: MapZoneRepository,
    request: Request,
    zone_id: int = Path(..., ge=1),
) -> JsonApiResponse[MapZoneResource]:
    """Get a zone by ID"""
    zone = await map_zone_repository.get_map_zone(zone_id)

    base_url = str(request.base_url).rstrip("/")
    resource_url = f"{base_url}/v1/zones/{zone_id}"

    return JsonApiResponse(
        data=MapZoneResource.from_db_model(zone, resource_url),
        links=JsonApiLinks(self_link=resource_url),
    )


@router.post(
    "/", response_model=JsonApiResponse[MapZoneResource], status_code=status.HTTP_201_CREATED
)
async def create_zone(
    _: Annotated[db_models.User, Security(security_check, scopes=["admin"])],
    map_zone_repository: MapZoneRepository,
    request: Request,
    zone_data: MapZoneCreate,
) -> JsonApiResponse[MapZoneResource]:
    """Create a new zone"""
    zone_data_dict = zone_data.model_dump()
    zone = await map_zone_repository.create_map_zone(zone_data_dict)

    base_url = str(request.base_url).rstrip("/")
    resource_url = f"{base_url}/v1/zones/{zone.id}"

    return JsonApiResponse(
        data=MapZoneResource.from_db_model(zone, resource_url),
        links=JsonApiLinks(self_link=resource_url),
    )


@router.patch("/{zone_id}", response_model=JsonApiResponse[MapZoneResource])
async def update_zone(
    _: Annotated[db_models.User, Security(security_check, scopes=["admin"])],
    map_zone_repository: MapZoneRepository,
    request: Request,
    zone_data: MapZoneUpdate,
    zone_id: int = Path(..., ge=1),
) -> JsonApiResponse[MapZoneResource]:
    """Update a zone by ID"""
    zone_data_dict = zone_data.model_dump(exclude_unset=True)
    zone = await map_zone_repository.update_map_zone(zone_id, zone_data_dict)

    base_url = str(request.base_url).rstrip("/")
    resource_url = f"{base_url}/v1/zones/{zone_id}"

    return JsonApiResponse(
        data=MapZoneResource.from_db_model(zone, resource_url),
        links=JsonApiLinks(self_link=resource_url),
    )


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
    _: Annotated[db_models.Admin, Security(security_check, scopes=["admin"])],
    zone_type_repository: ZoneTypeRepository,
    request: Request,
    zone_type_data: ZoneTypeCreate,
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
    _: Annotated[db_models.Admin, Security(security_check, scopes=["admin"])],
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

@router.post("/point_in_zone", response_model=JsonApiResponse[MapZoneResource])
async def get_point_in_zone(
    map_zone_repository: MapZoneRepository,
    request: Request,
    point: WKTPoint
) -> JsonApiResponse[MapZoneResource]:
    """Get a zone by point"""
    zone = await map_zone_repository.check_if_point_in_zones(point)

    base_url = str(request.base_url).rstrip("/")
    resource_url = f"{base_url}/v1/zones/{zone.id}"

    return JsonApiResponse(
        data=MapZoneResource.from_db_model(zone, resource_url),
        links=JsonApiLinks(self_link=resource_url),
    )
