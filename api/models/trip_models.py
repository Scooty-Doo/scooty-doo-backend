"""Module for trip models"""

from datetime import datetime
from typing import Annotated, Any, Generic, Optional, TypeVar
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from api.models.models import WKTPoint, JsonApiLinks, JsonApiResponse

class TripAttributes(BaseModel):
    """Trip attributes for JSON:API response."""

    # FOr now just use string for path_taken to simplify
    # Set Optional and a default value for any nullable field in db
    start_position: WKTPoint
    end_position: Optional[WKTPoint] = None
    path_taken: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    #Confloat deprecated, see: https://docs.pydantic.dev/2.10/api/types/#pydantic.types.confloat
    start_fee: Optional[Annotated[float, Field(ge=0)]] = None
    time_fee: Optional[Annotated[float, Field(ge=0)]] = None
    end_fee: Optional[Annotated[float, Field(ge=0)]] = None
    total_fee: Optional[Annotated[float, Field(ge=0)]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TripRelationships(BaseModel):
    """Trip relationships for JSON:API response."""

    user: dict[str, Any]
    bike: dict[str, Any]
    # Change to optional and set default to None since each trip doesnt have a transaction
    transaction: Optional[dict[str, Any]] = None


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
        relationships = {
            "user": {"data": {"type": "users", "id": str(trip.user_id)}},
            "bike": {"data": {"type": "bikes", "id": str(trip.bike_id)}},
        }

        # Add transaction only if it exists
        if hasattr(trip, 'transaction') and trip.transaction is not None:
            relationships["transaction"] = {
                "data": {"type": "transactions", "id": str(trip.transaction.id)}
            }

        return cls(
            id=str(trip.id),
            attributes=TripAttributes.model_validate(trip),
            relationships=TripRelationships(**relationships),
            # Add links to user/bike/transaction?
            links=JsonApiLinks(self_link=f"{request_url}"),
        )

class TripCreate(BaseModel):
    """Model for creating a new trip"""
    bike_id: int
    user_id: int
    start_position: WKTPoint

class UserTripStart(BaseModel):
    """Model for starting a trip"""
    user_id: int
    bike_id: int

class TripEnd(BaseModel):
    """Model for ending a trip"""
    end_position: WKTPoint
    path_taken: str
    end_time: datetime

# class TripEnd(BaseModel):
#     """Model for ending a trip"""
#     end_position: WKTPoint = Field(
#         None,
#         description="WKT POINT format, e.g. 'POINT(57.7089 11.9746)'",
#     )
#     path_taken: str = Field(
#         None,
#         description="WKT LINESTRING format, e.g. 'LINESTRING(57.7089 11.9746, 57.7089 11.9746)'",
#     )
#     end_time: datetime
#     end_fee: Annotated[float, Field(gt=0)]
#     total_fee: Annotated[float, Field(gt=0)]
