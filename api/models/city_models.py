"""Models for zone types and map zones."""

# TODO: Create pydantic model for boundaries (for now just strings)
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from api.models.models import JsonApiLinks
from api.models.wkt_models import WKTPoint


class CityAttributes(BaseModel):
    """City attributes for JSON:API response."""

    city_name: str
    country_code: str = Field(..., min_length=3, max_length=3)
    c_location: WKTPoint

    model_config = ConfigDict(from_attributes=True)


class CityResource(BaseModel):
    """JSON:API resource object for cities."""

    id: str
    type: str = "cities"
    attributes: CityAttributes
    links: Optional[JsonApiLinks] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_db_model(cls, city: Any, base_url: str) -> "CityResource":
        """Create a CityResource from a database model."""
        return cls(
            id=str(city.id),
            attributes=CityAttributes.model_validate(city),
            links=JsonApiLinks(self_link=f"{base_url}/v1/bikes/available?city_id={city.id}"),
        )


class CityGetRequestParams(BaseModel):
    """Query parameters for GET requests to /cities."""

    city_name_search: Optional[str] = None
    city_id: Optional[int] = None

    model_config = ConfigDict(populate_by_alias=True)
