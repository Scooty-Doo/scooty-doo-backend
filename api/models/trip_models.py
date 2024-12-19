"""Module for trip models"""

from datetime import datetime
from typing import Annotated, Any, Generic, Optional, TypeVar
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from models import WKTPoint, JsonApiLinks

class TripAttributes(BaseModel):
    """Trip attributes for JSON:API response."""


    start_position: WKTPoint
    end_position: Optional[WKTPoint] = Field(
        None
    )
    path_taken: Optional[str] # this needs to be converted
    start_time: datetime
    end_time: Optional[datetime]
    start_fee: float # Should be confloat, but I couldn't wrap my head around it
    time_fee: Optional[float]
    end_fee: Optional[float]
    total_fee: Optional[float]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class TripRelationships(BaseModel):
    """Trip relationships for JSON:API response."""

    user: dict[str, Any]
    bike: dict[str, Any]
    transaction: dict[str, Any] # list? Should this be different?


class TripResource(BaseModel):
    """JSON:API resource object for trips."""

    id: str
    type: str = "trips"
    attributes: TripAttributes
    relationships: Optional[TripRelationships] = None
    links: Optional[JsonApiLinks] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_db_model(cls, trip: Any, request_url: str) -> "TripResource":
        """Create a TripResource from a database model."""
        return cls(
            id=str(trip.id),
            attributes=TripAttributes.model_validate(trip),
            relationships=TripRelationships(
                city={
                    "data": 
                      {
                          {"type": "user", "id": str(trip.user_id)},
                          {"type": "bike", "id": str(trip.bike_id)},
                          {"type": "transaction", "id": str(trip.transaction_id)} # This is a list? Syntax? For loop?
                      }
            }),
            links=JsonApiLinks(self_link=f"{request_url}{trip.id}"),
        )


class TripCreate(BaseModel):
    """Model for creating a new trip"""
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
    """


class TripUpdate(BaseModel):
    """Model for updating an existing trip"""
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
    """
