"""Module for pydantic models"""

# pylint: disable=too-few-public-methods
import re
from datetime import datetime
from typing import Annotated, Any, Generic, Optional, TypeVar

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


def validate_wkt_point(value: str | None) -> str | None:
    """Validate WKT POINT format and coordinates."""
    if value is None:
        return None

    point_pattern = r"^POINT\(\s*(-?\d+(\.\d+)?|-?\d+\.\d+)\s+(-?\d+(\.\d+)?|-?\d+\.\d+)\s*\)$"
    match = re.match(point_pattern, str(value))

    if not match:
        raise ValueError(f"Invalid WKT POINT format: {value}")

    longitude, latitude = map(float, match.groups()[0:2])

    if not -180 <= longitude <= 180:
        raise ValueError(f"Longitude {longitude} out of range [-180, 180]")
    if not -90 <= latitude <= 90:
        raise ValueError(f"Latitude {latitude} out of range [-90, 90]")

    return value


WKTPoint = Annotated[str, BeforeValidator(validate_wkt_point)]


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
        description="WKT POINT format, e.g. 'POINT(57.7089 11.9746)'",
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
            links=JsonApiLinks(self_link=f"{request_url}/{bike.id}"),
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


class PaymentProvider(BaseModel):
    """Model for payment provider table in database"""

    id: int
    provider_name: str
    metadata: str  # JSON
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?


class PaymentMethod(BaseModel):
    """Model for payment method table in database"""

    id: int
    user: "User"
    provider: PaymentProvider
    provider_specific_id: str
    is_active: bool
    is_default: bool
    metadata: str  # JSON
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?


class Trip(BaseModel):
    """Model for trip table in database"""

    id: int
    bike_id: int
    user_id: int
    start_time: datetime.datetime  # timestamp?
    end_time: datetime.datetime  # timestamp?
    start_position: list[float]  # import some type?
    end_position: list[float]  # import some type?
    path_taken: str  # Linestring - import some type?
    start_fee: float
    time_fee: float
    end_fee: float
    total_fee: float
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?


class Transaction(BaseModel):
    """Model for transaction table in database"""

    id: int
    user: "User"
    amount: float
    transtion_type: str
    transaction_description: str
    trip: Trip
    metadata: str  # JSON
    payment_method: PaymentMethod
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?


class User(BaseModel):
    """Model for user table in database"""

    id: int
    full_name: str
    email: str
    balance: float
    use_prepay: bool
    metadata: str
    payment_methods: list[PaymentMethod]  # Should work?
    trips: list[Trip]
    transactions: list[Transaction]
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?


class City(BaseModel):
    """Model for city table in database"""

    id: int
    city_name: str
    country_code: str
    c_location: str  # position
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?


class Zone(BaseModel):
    """Model for zone table in database"""

    id: int
    zone_name: str
    zone_type: "ZoneType"
    city: City
    boundary: str
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?


class ZoneType(BaseModel):
    """Model for zone type table in database"""

    id: int
    type_name: str
    speed_limit: int
    start_fee: float
    end_fee: float
    metadata: str  # JSON
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?


class AdminRoles(BaseModel):
    """Model for admin roles table in database"""

    id: int
    role_name: str
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?


class Admin:
    """Model for admin table in database"""

    id: int
    full_name: str
    email: str
    metadata: str  # JSON
    created_at: datetime.datetime  # timestamp?
    updated_at: datetime.datetime  # timestamp?
    roles: list[AdminRoles]
