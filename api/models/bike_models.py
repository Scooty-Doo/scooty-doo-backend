"""Models for bikes"""

from typing import Optional, Any

from pydantic import Field, field_validator, BaseModel, ConfigDict

from datetime import datetime
from api.models.models import JsonApiLinks
from api.models.wkt_models import WKTPoint


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
    TODO: Either convert battery_lvl to battery_level or update the database column name
    """

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
    TODO: Either convert battery_lvl to battery_level or update the database column name
    """

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


class BikeSocket(BikeUpdate):
    """Socket output model"""

    bike_id: int
    zone_id: Optional[int] = Field(alias="end_map_zone_id", default=None)
    zone_type: Optional[str] = Field(alias="end_map_zone_type", default=None)

    @field_validator("battery_lvl", mode="before")
    @classmethod
    def cast_float_to_int(cls, value: float) -> int:
        """Casts battery_lvl to int"""
        return int(value)