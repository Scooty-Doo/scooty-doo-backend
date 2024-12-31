"""Models for zone types and map zones."""
#TODO: Create pydantic model for boundaries (for now just strings)
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from api.models.models import JsonApiLinks


class ZoneTypeAttributes(BaseModel):
    """ZoneType attributes for JSON:API response."""
    type_name: str
    speed_limit: int
    start_fee: float
    end_fee: float
    meta_data: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# Should relationships be included? (for now not included)
class ZoneTypeResource(BaseModel):
    """JSON:API resource object for zone types."""
    id: str
    type: str = "zone_types"
    attributes: ZoneTypeAttributes
    links: Optional[JsonApiLinks] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_db_model(cls, zone_type: Any, request_url: str) -> "ZoneTypeResource":
        relationships = {}
        if hasattr(zone_type, "zones") and zone_type.zones is not None:
            relationships["zones"] = {
                "data": [{"type": "map_zones", "id": str(zone.id)} for zone in zone_type.zones]
            }
        return cls(
            id=str(zone_type.id),
            attributes=ZoneTypeAttributes.model_validate(zone_type),
            links=JsonApiLinks(self_link=f"{request_url}")
        )

class ZoneTypeCreate(BaseModel):
    """Model for creating a zone type."""
    type_name: str
    speed_limit: Optional[int] = None
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

# Should relationships be included? (for now not included)
class MapZoneResource(BaseModel):
    """JSON:API resource object for map zones."""
    id: str
    type: str = "map_zones"
    attributes: MapZoneAttributes
    links: Optional[JsonApiLinks] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_db_model(cls, map_zone: Any, request_url: str) -> "MapZoneResource":
        relationships = {}
        if hasattr(map_zone, "zone_type") and map_zone.zone_type is not None:
            relationships["zone_type"] = {
                "data": {"type": "zone_types", "id": str(map_zone.zone_type.id)}
            }
        if hasattr(map_zone, "city") and map_zone.city is not None:
            relationships["city"] = {
                "data": {"type": "cities", "id": str(map_zone.city.id)}
            }
        return cls(
            id=str(map_zone.id),
            attributes=MapZoneAttributes.model_validate(map_zone),
            links=JsonApiLinks(self_link=f"{request_url}")
        )

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