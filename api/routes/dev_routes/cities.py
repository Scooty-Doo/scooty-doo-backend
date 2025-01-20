"""Module for the /cities routes"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from api.db.repository_city import (
    CityRepository as CityRepoClass,
)
from api.dependencies.repository_factory import get_repository
from api.models import db_models
from api.models.city_models import (
    CityGetRequestParams,
    CityResource,
)
from api.models.models import (
    JsonApiLinks,
    JsonApiResponse,
)

router = APIRouter(
    prefix="/dev/cities",
    tags=["cities"],
    responses={404: {"description": "Not found"}},
)

CityRepository = Annotated[
    CityRepoClass,
    Depends(get_repository(db_models.City, repository_class=CityRepoClass)),
]


@router.get("/", response_model=JsonApiResponse[CityResource])
async def get_cities(
    request: Request,
    city_repository: CityRepository,
    query_params: CityGetRequestParams = Depends(),
) -> JsonApiResponse[CityResource]:
    """Get cities from the db"""
    cities = await city_repository.get_cities(**query_params.model_dump(exclude_none=True))
    base_url = str(request.base_url).rstrip("/")
    collection_url = f"{base_url}/dev/cities"

    return JsonApiResponse(
        data=[CityResource.from_db_model(city, base_url) for city in cities],
        links=JsonApiLinks(self_link=collection_url),
    )
