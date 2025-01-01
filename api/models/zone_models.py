"""Models for zone types and map zones."""

# TODO: Create pydantic model for boundaries (for now just strings)
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from api.models.models import JsonApiLinks
from api.models.city_models import CityResource, CityAttributes


class ZoneTypeAttributes(BaseModel):
    """ZoneType attributes for JSON:API response."""

    type_name: str
    speed_limit: int
    start_fee: float
    end_fee: float
    meta_data: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# Should relationships be included? (for now not included)
class ZoneTypeResource(BaseModel):
    """JSON:API resource object for zone types."""

    id: str
    type: str = "zone_types"
    attributes: ZoneTypeAttributes
    links: Optional[JsonApiLinks] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_db_model(cls, zone_type: Any, request_url: str) -> "ZoneTypeResource":
        """Create a ZoneTypeResource from a database model."""
        return cls(
            id=str(zone_type.id),
            attributes=ZoneTypeAttributes.model_validate(zone_type),
            links=JsonApiLinks(self_link=f"{request_url}"),
        )


class ZoneTypeCreate(BaseModel):
    """Model for creating a zone type."""

    type_name: str
    speed_limit: int
    start_fee: float
    end_fee: float
    meta_data: Optional[dict] = None


class ZoneTypeUpdate(BaseModel):
    """Model for updating a zone type."""

    type_name: Optional[str] = None
    speed_limit: Optional[int] = None
    start_fee: Optional[float] = None
    end_fee: Optional[float] = None
    meta_data: Optional[dict] = None


class MapZoneAttributes(BaseModel):
    """MapZone attributes for JSON:API response."""

    zone_name: str
    # WKT POLYGON format
    boundary: str
    city_id: int
    zone_type_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MapZoneRelationships(BaseModel):
    """MapZone relationships for JSON:API response."""

    city: Optional[dict[str, Any]] = None
    zone_type: Optional[dict[str, Any]] = None

    model_config = ConfigDict(populate_by_name=True)


class MapZoneResourceMinimal(BaseModel):
    """JSON:API resource object for map zones without relationships."""

    id: str
    type: str = "map_zones"
    attributes: MapZoneAttributes
    links: Optional[JsonApiLinks] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_db_model(cls, map_zone: Any, request_url: str) -> "MapZoneResourceMinimal":
        """Create a minimal MapZoneResource from a database model."""
        return cls(
            id=str(map_zone.id),
            attributes=MapZoneAttributes.model_validate(map_zone),
            links=JsonApiLinks(self_link=f"{request_url}"),
        )


class MapZoneResource(BaseModel):
    """JSON:API resource object for map zones."""
    id: str
    type: str = "map_zones"
    attributes: MapZoneAttributes
    relationships: MapZoneRelationships
    links: Optional[JsonApiLinks] = None

    @classmethod
    def from_db_model(cls, map_zone: Any, request_url: str) -> "MapZoneResource":
        """Create a MapZoneResource from a database model."""
        base_url = str(request_url).rsplit("/v1/zones/", 1)[0]
        
        relationships = {
            "city": {
                "data": {"type": "cities", "id": str(map_zone.city_id)},
                "links": {
                    "self": f"{base_url}/v1/cities/{map_zone.city_id}"
                }
            },
            "zone_type": {
                "data": {"type": "zone_types", "id": str(map_zone.zone_type_id)},
                "links": {
                    "self": f"{base_url}/v1/zone-types/{map_zone.zone_type_id}"
                }
            }
        }

        return cls(
            id=str(map_zone.id),
            attributes=MapZoneAttributes.model_validate(map_zone),
            relationships=relationships,
            links=JsonApiLinks(self_link=request_url)
        )

class MapZoneGetRequestParams(BaseModel):
    """Model for request parameters for getting map zones."""

    # Pagination and offset
    limit: int = Field(100, gt=0)
    offset: int = Field(0, ge=0)

    # Sorting
    order_by: Literal["created_at", "updated_at", "zone_name", "city_id", "zone_type_id"] = (
        "city_id"
    )
    order_direction: Literal["asc", "desc"] = "asc"

    # Parameters for filtering
    zone_name_search: Optional[str] = Field(None, min_length=3)
    city_id: Optional[int] = None
    zone_type_id: Optional[int] = None
    created_at_gt: Optional[datetime] = None
    created_at_lt: Optional[datetime] = None
    updated_at_gt: Optional[datetime] = None
    updated_at_lt: Optional[datetime] = None


class MapZoneCreate(BaseModel):
    """Model for creating a map zone."""

    zone_name: str
    zone_type_id: int
    city_id: int
    boundary: str


class MapZoneUpdate(BaseModel):
    """Model for updating a map zone."""

    zone_name: Optional[str] = None
    zone_type_id: Optional[int] = None
    city_id: Optional[int] = None
    boundary: Optional[str] = None
