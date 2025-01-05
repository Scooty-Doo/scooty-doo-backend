"""Module for pydantic models
Note: JSON:API integration with FastAPI feels clunky.
use a library like fastapi-jsonapi?
https://fastapi-jsonapi.readthedocs.io/en/latest/
"""

# pylint: disable=too-few-public-methods
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from api.models.wkt_models import WKTPoint


class JsonApiLinks(BaseModel):
    """JSON:API links object."""

    self_link: str = Field(..., alias="self")

    model_config = ConfigDict(populate_by_name=True)


class JsonApiError(BaseModel):
    """JSON:API error object."""

    status: str
    title: str
    detail: Optional[str] = None


class JsonApiErrorResponse(BaseModel):
    """JSON:API error response."""

    errors: list[JsonApiError]


T = TypeVar("T", bound=BaseModel)


class JsonApiResponse(BaseModel, Generic[T]):
    """JSON:API response wrapper."""

    data: T | list[T]
    links: JsonApiLinks


class BikeAttributes(BaseModel):
    """Bike attributes for JSON:API response."""

    battery_level: int = Field(ge=0, le=100, alias="battery_lvl")
    position: Optional[WKTPoint] = Field(
        None,
        alias="last_position",
    )
    is_available: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class BikeRelationships(BaseModel):
    """Bike relationships for JSON:API response."""

    city: dict[str, Any]


class BikeResource(BaseModel):
    """JSON:API resource object for bikes."""

    id: str
    type: str = "bikes"
    attributes: BikeAttributes
    relationships: Optional[BikeRelationships] = None
    links: Optional[JsonApiLinks] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_db_model(cls, bike: Any, request_url: str) -> "BikeResource":
        """Create a BikeResource from a database model."""
        return cls(
            id=str(bike.id),
            attributes=BikeAttributes.model_validate(bike),
            relationships=BikeRelationships(
                city={"data": {"type": "cities", "id": str(bike.city_id)}}
            ),
            links=JsonApiLinks(self_link=f"{request_url}{bike.id}"),
        )


class BikeCreate(BaseModel):
    """Model for creating a new bike
    TODO: Either convert battery_lvl to battery_level or update the database column name"""

    battery_lvl: int = Field(ge=0, le=100)
    city_id: int
    last_position: Optional[WKTPoint] = Field(
        None,
        description="WKT POINT format, e.g. 'POINT(57.7089 11.9746)'",
    )
    is_available: bool = True
    meta_data: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class BikeUpdate(BaseModel):
    """Model for updating an existing bike
    TODO: Either convert battery_lvl to battery_level or update the database column name"""

    battery_lvl: Optional[int] = Field(None, ge=0, le=100, alias="battery_lvl")
    city_id: Optional[int] = None
    last_position: Optional[WKTPoint] = Field(
        None,
        description="WKT POINT format, e.g. 'POINT(57.7089 11.9746)'",
        alias="last_position",
    )
    is_available: Optional[bool] = None
    meta_data: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
