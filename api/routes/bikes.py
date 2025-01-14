"""Module for the /bikes routes"""

# Filtering with query params seems clunky. Could it be done easier? Perhaps one of these:
# https://github.com/arthurio/fastapi-filter
# https://github.com/OleksandrZhydyk/FastAPI-SQLAlchemy-Filters
#
# TODO: Should probably add pydantic type checks to query params?
# Otherwise, the db might go through a lot of work for nothing if the query params are invalid.
# TODO: Admin checks
# TODO: Pagination
# TODO: Fix update
# TODO: Error handling
# TODO: Efficient query param handling

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, Security

from api.db.repository_bike import BikeRepository as BikeRepoClass
from api.dependencies.repository_factory import get_repository
from api.models import db_models
from api.models.bike_models import (
    BikeCreate,
    BikeResource,
    BikeSocket,
    BikeUpdate,
)
from api.models.models import (
    JsonApiError,
    JsonApiErrorResponse,
    JsonApiLinks,
    JsonApiResponse,
)
from api.services.socket import emit_update
from api.services.oauth import security_check

router = APIRouter(
    prefix="/v1/bikes",
    tags=["bikes"],
    responses={
        404: {
            "model": JsonApiErrorResponse,
            "description": "Resource not found",
            "content": {
                "application/json": {
                    "example": {
                        "errors": [
                            {
                                "status": "404",
                                "title": "Resource not found",
                                "detail": "The requested bike was not found",
                            }
                        ]
                    }
                }
            },
        },
        422: {
            "model": JsonApiErrorResponse,
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "errors": [
                            {
                                "status": "422",
                                "title": "Validation Error",
                                "detail": "The field 'battery_lvl' must be between 0 and 100",
                            }
                        ]
                    }
                }
            },
        },
    },
)

BikeRepository = Annotated[
    BikeRepoClass,
    Depends(get_repository(db_models.Bike, repository_class=BikeRepoClass)),
]


def raise_not_found(detail: str):
    """Raise a 404 error in JSON:API format.
    TODO: Change to work the same way as validation error? Move to exceptions?"""
    raise HTTPException(
        status_code=404,
        detail=JsonApiErrorResponse(
            errors=[JsonApiError(status="404", title="Resource not found", detail=detail)]
        ).model_dump(),
    )


@router.get("/", response_model=JsonApiResponse[BikeResource])
async def get_all_bikes(
    _: Annotated[int, Security(security_check, scopes=["admin"])],
    request: Request,
    bike_repository: BikeRepository,
    city_id: Annotated[int | None, Query()] = None,
    min_battery: Annotated[int | None, Query(ge=0, le=100)] = None,
    max_battery: Annotated[int | None, Query(ge=0, le=100)] = None,
) -> JsonApiResponse[BikeResource]:
    """Get all bikes (admin only)."""
    filters = {}
    if city_id is not None:
        filters["city_id"] = city_id
    if min_battery is not None:
        filters["min_battery"] = min_battery
    if max_battery is not None:
        filters["max_battery"] = max_battery

    bikes = await bike_repository.get_bikes(filters)
    base_url = str(request.base_url).rstrip("/") + request.url.path

    return JsonApiResponse(
        data=[BikeResource.from_db_model(bike, base_url) for bike in bikes],
        links=JsonApiLinks(self_link=base_url.rsplit("/", 1)[0]),
    )


@router.get("/available", response_model=JsonApiResponse[BikeResource])
async def get_available_bikes(
    request: Request,
    bike_repository: BikeRepository,
    city_id: Annotated[int | None, Query()] = None,
    min_battery: Annotated[int | None, Query(ge=0, le=100)] = None,
    max_battery: Annotated[int | None, Query(ge=0, le=100)] = None,
) -> JsonApiResponse[BikeResource]:
    """Get all available bikes.
    TODO: Should probably add pydantic type checks to query params?
    TODO: Find more efficient way to filter parameters??"""
    filters = {"is_available": True}

    if city_id is not None:
        filters["city_id"] = city_id
    if min_battery is not None:
        filters["min_battery"] = min_battery
    if max_battery is not None:
        filters["max_battery"] = max_battery

    bikes = await bike_repository.get_bikes(filters)
    base_url = str(request.base_url).rstrip("/") + request.url.path

    return JsonApiResponse(
        data=[BikeResource.from_db_model(bike, base_url) for bike in bikes],
        links=JsonApiLinks(self_link=base_url.rsplit("/", 1)[0]),
    )


@router.get("/{bike_id}", response_model=JsonApiResponse[BikeResource])
async def get_bike(
    _: Annotated[int, Security(security_check, scopes=["admin"])],
    request: Request, bike_id: int, bike_repository: BikeRepository,
) -> JsonApiResponse[BikeResource]:
    """Get a bike by ID."""
    bike = await bike_repository.get_bike(bike_id)
    if bike is None:
        raise_not_found(f"Bike with ID {bike_id} not found")

    base_url = str(request.base_url).rstrip("/") + request.url.path
    base_url = base_url.rsplit("/", 1)[0] + "/"
    self_link = base_url + str(bike_id)

    return JsonApiResponse(
        data=BikeResource.from_db_model(bike, base_url),
        links=JsonApiLinks(self_link=self_link),
    )


@router.post(
    "/",
    response_model=JsonApiResponse[BikeResource],
    status_code=status.HTTP_201_CREATED
)
async def add_bike(
    _: Annotated[int, Security(security_check, scopes=["admin"])],
    request: Request,
    bike: BikeCreate,
    bike_repository: BikeRepository,
) -> JsonApiResponse[BikeResource]:
    """Add a new bike to the database (admin only)"""
    bike_data = bike.model_dump()
    created_bike = await bike_repository.add_bike(bike_data)

    base_url = str(request.base_url).rstrip("/") + "/v1/bikes"
    return JsonApiResponse(
        data=BikeResource.from_db_model(created_bike, base_url),
        links=JsonApiLinks(self_link=f"{base_url}/{created_bike.id}"),
    )


@router.patch("/{bike_id}", response_model=JsonApiResponse[BikeResource])
async def update_bike(
    _: Annotated[int, Security(security_check, scopes=["admin"])],
    request: Request,
    bike_id: int,
    bike_update: BikeUpdate,
    bike_repository: BikeRepository,
) -> JsonApiResponse[BikeResource]:
    """Update a bike."""
    bike = await bike_repository.get(bike_id)
    if bike is None:
        raise_not_found(f"Bike with ID {bike_id} not found")
    update_data = bike_update.model_dump(exclude_unset=True)
    updated_bike = await bike_repository.update_bike(bike_id, update_data)
    if updated_bike is None:
        raise_not_found(f"Failed to update bike with ID {bike_id}")

    base_url = str(request.base_url).rstrip("/") + request.url.path.rsplit("/", 1)[0]

    # Is this unpacking ok?
    await emit_update(BikeSocket(**updated_bike.__dict__, bike_id=bike_id))

    return JsonApiResponse(
        data=BikeResource.from_db_model(updated_bike, base_url),
        links=JsonApiLinks(self_link=base_url),
    )


@router.delete("/{bike_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_bike(
    _: Annotated[int, Security(security_check, scopes=["admin"])],
    bike_id: int,
    bike_repository: BikeRepository,
):
    """Remove a bike."""
    bike = await bike_repository.get(bike_id)
    if bike is None:
        raise_not_found(f"Bike with ID {bike_id} not found")

    await bike_repository.delete(bike_id)
