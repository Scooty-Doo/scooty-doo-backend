"""Models for zone types and map zones."""

# TODO: Create pydantic model for boundaries (for now just strings)
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict

from api.models.models import JsonApiLinks
from api.models.wkt_models import WKTPoint

class CityAttributes(BaseModel):
    """City attributes for JSON:API response."""
    city_name: str
    country_code: str
    c_location: WKTPoint
    
    model_config = ConfigDict(from_attributes=True)

class CityResource(BaseModel):
    """JSON:API resource object for cities."""
    id: str
    type: str = "cities"
    attributes: CityAttributes
    links: Optional[JsonApiLinks] = None