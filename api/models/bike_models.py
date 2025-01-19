"""Models for bikes"""

from datetime import datetime
from typing import Any, Literal, Optional, Union

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from api.models.models import JsonApiLinks
from api.models.wkt_models import WKTPoint


class UserBikeAttributes(BaseModel):
    """Bike attributes visible to users."""

    battery_level: int = Field(ge=0, le=100, alias="battery_lvl")
    position: Optional[WKTPoint] = Field(None, alias="last_position")
    is_available: bool = True

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminBikeAttributes(UserBikeAttributes):
    """Bike attributes visible to admins."""

    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class BikeRelationships(BaseModel):
    """Bike relationships for JSON:API response."""

    city: dict[str, Any]


class BikeZoneRelationships(BaseModel):
    zone: Optional[dict[str, Any]] = None


class BikeResource(BaseModel):
    """JSON:API resource object for bikes."""

    id: str
    type: str = "bikes"
    attributes: Union[UserBikeAttributes, AdminBikeAttributes]
    relationships: Optional[Union[BikeRelationships, BikeZoneRelationships]] = None
    links: Optional[JsonApiLinks] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_db_model(cls, bike: Any, request_url: str, is_admin: bool) -> "BikeResource":
        """Create a BikeResource from a database model."""
        attributes_model = AdminBikeAttributes if is_admin else UserBikeAttributes
        return cls(
            id=str(bike.id),
            attributes=attributes_model.model_validate(bike),
            relationships=BikeRelationships(
                city={"data": {"type": "cities", "id": str(bike.city_id)}}
            ),
            links=JsonApiLinks(self_link=f"{request_url}{bike.id}"),
        )

    @classmethod
    def from_bike_zone_model(
        cls, bike: Any, request_url: str, map_zone_id: int, is_admin: bool
    ) -> "BikeResource":
        """Create a BikeResource from a database model."""
        attributes_model = AdminBikeAttributes if is_admin else UserBikeAttributes
        return cls(
            id=str(bike.id),
            attributes=attributes_model.model_validate(bike),
            relationships=BikeZoneRelationships(
                zone={"data": {"type": "zones", "id": str(map_zone_id)}}
            ),
            links=JsonApiLinks(self_link=f"{request_url}v1/bikes/{bike.id}"),
        )


class BikeGetRequestParams(BaseModel):
    """Model for query params for getting bikes"""

    # Pagination defaults to 100 users per page
    limit: int = Field(300, gt=0)
    offset: int = Field(0, ge=0)

    # Sorting
    order_by: Literal["id", "created_at", "updated_at", "city_id", "is_available"] = "created_at"
    order_direction: Literal["asc", "desc"] = "desc"

    city_id: Optional[int] = Field(None, ge=1)
    is_available: Optional[bool] = None
    min_battery: Optional[float] = None
    max_battery: Optional[float] = None
    created_at_gt: Optional[datetime] = None
    created_at_lt: Optional[datetime] = None
    updated_at_gt: Optional[datetime] = None
    updated_at_lt: Optional[datetime] = None
    include_deleted: Optional[bool] = False


class UserBikeGetRequestParams(BaseModel):
    """Model for query params for getting bikes"""

    # Pagination defaults to 100 users per page
    limit: int = Field(300, gt=0)
    offset: int = Field(0, ge=0)

    # Sorting
    order_by: Literal["id", "created_at", "updated_at", "city_id", "is_available"] = "created_at"
    order_direction: Literal["asc", "desc"] = "desc"

    city_id: Optional[int] = Field(None, ge=1)
    battery_gt: Optional[float] = None
    battery_lt: Optional[float] = None


class ZoneBikeGetRequestParams(BaseModel):
    zone_type_id: int = Field(gt=0)
    city_id: int = Field(gt=0)


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
    speed: Optional[float] = 0.0
    is_available: Optional[bool] = None
    meta_data: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @field_validator("battery_lvl", mode="before")
    @classmethod
    def cast_float_to_int(cls, value: float) -> int:
        """Casts battery_lvl to int"""
        return int(value)


class BikeSocket(BikeUpdate):
    """Socket output model for reports"""

    bike_id: int


class BikeSocketStartEnd(BikeSocket):
    """Socket output model for start/end trip"""

    zone_id: Optional[int] = Field(
        alias=AliasChoices("start_zone_map_id", "end_map_zone_id"), default=None
    )
