"""Module for pydantic models
Note: JSON:API integration with FastAPI feels clunky.
use a library like fastapi-jsonapi?
https://fastapi-jsonapi.readthedocs.io/en/latest/
"""

# pylint: disable=too-few-public-methods
import re
from datetime import datetime
from typing import Annotated, Any, Generic, Optional, TypeVar
from shapely import wkt
from shapely.errors import ShapelyError
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from shapely import wkt
from shapely.errors import ShapelyError
from typing import ClassVar

class WKTGeometry(str):
    """Base class for WKT geometry validation"""
    geometry_type: ClassVar[str] = ""
    
    @classmethod
    def validate_coordinates(cls, coords):
        """Validate coordinate bounds"""
        for x, y in coords:
            if not (-180 <= x <= 180 and -90 <= y <= 90):
                raise ValueError(
                    f'Invalid coordinates ({x}, {y}). '
                    'Longitude must be between -180 and 180, '
                    'Latitude must be between -90 and 90'
                )
    @classmethod
    def clean_wkt_format(cls, value: str) -> str:
        """Remove extra whitespace from WKT format"""
        pattern = rf'\b({cls.geometry_type})\s+\('
        cleaned = re.sub(pattern, r'LINESTRING(', value, flags=re.IGNORECASE)
        return cleaned

class WKTPoint(WKTGeometry):
    """Custom type for WKT Point validation"""
    geometry_type = "Point"
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, value, info):
        try:
            geom = wkt.loads(value)
            if geom.geom_type != cls.geometry_type:
                raise ValueError(f'Geometry must be a {cls.geometry_type}')
            cls.validate_coordinates([geom.coords[0]])
            return cls.clean_wkt_format(value)
        except ShapelyError as e:
            raise ValueError(f'Invalid WKT format: {str(e)}') from e
        except Exception as e:
            raise ValueError(f'Invalid {cls.geometry_type}: {str(e)}') from e

class WKTLineString(WKTGeometry):
    """Custom type for WKT LineString validation"""
    geometry_type = "LineString"
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, value, info):
        try:
            geom = wkt.loads(value)
            if geom.geom_type != cls.geometry_type:
                raise ValueError(f'Geometry must be a {cls.geometry_type}')
            cls.validate_coordinates(geom.coords)
            cleaned_value = cls.clean_wkt_format(value)
            return cleaned_value    
        except ShapelyError as e:
            raise ValueError(f'Invalid WKT format: {str(e)}') from e
        except Exception as e:
            raise ValueError(f'Invalid {cls.geometry_type}: {str(e)}') from e

class WKTPolygon(WKTGeometry):
    """Custom type for WKT Polygon validation"""
    geometry_type = "Polygon"
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, value, info):
        try:
            geom = wkt.loads(value)
            if geom.geom_type != cls.geometry_type:
                raise ValueError(f'Geometry must be a {cls.geometry_type}')

            # in case of more complex polygons with holes (interiors)
            for ring in geom.exterior.coords:
                cls.validate_coordinates([ring])
            for interior in geom.interiors:
                cls.validate_coordinates(interior.coords)
            return cls.clean_wkt_format(value)
        except ShapelyError as e:
            raise ValueError(f'Invalid WKT format: {str(e)}') from e
        except Exception as e:
            raise ValueError(f'Invalid {cls.geometry_type}: {str(e)}') from e

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
            links=JsonApiLinks(self_link=f"{request_url}"),
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


# class PaymentProvider(BaseModel):
#     """Model for payment provider table in database"""

#     id: int
#     provider_name: str
#     metadata: str  # JSON
#     created_at: datetime
#     updated_at: datetime


# class PaymentMethod(BaseModel):
#     """Model for payment method table in database"""

#     id: int
#     user: "User"
#     provider: PaymentProvider
#     provider_specific_id: str
#     is_active: bool
#     is_default: bool
#     metadata: str  # JSON
#     created_at: datetime
#     updated_at: datetime


# class Trip(BaseModel):
#     """Model for trip table in database"""

#     id: int
#     bike_id: int
#     user_id: int
#     start_time: datetime
#     end_time: datetime
#     start_position: list[float]  # Use list for type hinting
#     end_position: list[float]  # Use list for type hinting
#     path_taken: str  # Linestring - import some type?
#     start_fee: float
#     time_fee: float
#     end_fee: float
#     total_fee: float
#     created_at: datetime
#     updated_at: datetime


# class Transaction(BaseModel):
#     """Model for transaction table in database"""

#     id: int
#     user: "User"
#     amount: float
#     transaction_type: str
#     transaction_description: str
#     trip: Trip
#     metadata: str  # JSON
#     payment_method: PaymentMethod
#     created_at: datetime
#     updated_at: datetime


# class User(BaseModel):
#     """Model for user table in database"""

#     id: int
#     full_name: str
#     email: str
#     balance: float
#     use_prepay: bool
#     metadata: str
#     payment_methods: list[PaymentMethod]  # Use list for type hinting
#     trips: list[Trip]  # Use list for type hinting
#     transactions: list[Transaction]  # Use list for type hinting
#     created_at: datetime
#     updated_at: datetime


# class City(BaseModel):
#     """Model for city table in database"""

#     id: int
#     city_name: str
#     country_code: str
#     c_location: str  # position
#     created_at: datetime
#     updated_at: datetime


# class Zone(BaseModel):
#     """Model for zone table in database"""

#     id: int
#     zone_name: str
#     zone_type: "ZoneType"
#     city: City
#     boundary: str
#     created_at: datetime
#     updated_at: datetime


# class ZoneType(BaseModel):
#     """Model for zone type table in database"""

#     id: int
#     type_name: str
#     speed_limit: int
#     start_fee: float
#     end_fee: float
#     metadata: str  # JSON
#     created_at: datetime
#     updated_at: datetime


# class AdminRoles(BaseModel):
#     """Model for admin roles table in database"""

#     id: int
#     role_name: str
#     created_at: datetime
#     updated_at: datetime


# class Admin(BaseModel):
#     """Model for admin table in database"""

#     id: int
#     full_name: str
#     email: str
#     metadata: str  # JSON
#     created_at: datetime
#     updated_at: datetime
#     roles: list[AdminRoles]  # Use list for type hinting
