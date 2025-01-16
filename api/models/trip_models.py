"""Module for trip models"""

from datetime import datetime
from typing import Annotated, Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from api.models.models import JsonApiLinks
from api.models.wkt_models import WKTLineString, WKTPoint

TripId = Annotated[int, Field(gt=0, description="Trip ID")]


class TripAttributes(BaseModel):
    """Trip attributes for JSON:API response."""

    # FOr now just use string for path_taken to simplify
    # Set Optional and a default value for any nullable field in db
    start_position: WKTPoint
    end_position: Optional[WKTPoint] = None
    path_taken: Optional[WKTLineString] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    # Confloat deprecated, see: https://docs.pydantic.dev/2.10/api/types/#pydantic.types.confloat
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

    id: int
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
        if hasattr(trip, "transaction") and trip.transaction is not None:
            relationships["transaction"] = {
                "data": {"type": "transactions", "id": str(trip.transaction.id)}
            }

        return cls(
            id=str(trip.id),
            attributes=TripAttributes.model_validate(trip),
            relationships=TripRelationships(**relationships),
            # Add links to user/bike/transaction?
            links=JsonApiLinks(self_link=f"{request_url}{trip.id}"),
        )


class UserTripStart(BaseModel):
    """Model for starting a trip"""

    user_id: int
    bike_id: int


class BikeTripReport(BaseModel):
    """Bike status report from bike service."""

    city_id: int
    last_position: WKTPoint
    battery_lvl: float
    is_available: bool


class BikeTripStartlog(BaseModel):
    """Trip log from bike service."""

    bike_id: int
    trip_id: int
    start_time: datetime
    start_position: WKTPoint
    path_taken: Optional[WKTLineString] = None
    start_map_zone_id: Optional[int] = None
    start_map_zone_type: Optional[str] = None


class BikeTripEndLog(BikeTripStartlog):
    """Trip log from bike service."""

    user_id: int
    end_time: datetime
    end_position: WKTPoint
    path_taken: WKTLineString
    end_map_zone_id: Optional[int] = None
    end_map_zone_type: Optional[str] = None


class BikeTripStartData(BaseModel):
    """Combined bike data from service."""

    report: BikeTripReport
    log: BikeTripStartlog


class BikeTripEndData(BaseModel):
    """Combined bike data from service."""

    report: BikeTripReport
    log: BikeTripEndLog


class TripCreate(BaseModel):
    """Data required to create a new trip."""

    id: int
    user_id: int
    bike_id: int
    start_position: WKTPoint


class TripEndRepoParams(BaseModel):
    """Model for ending a trip"""

    end_position: WKTPoint
    path_taken: WKTLineString
    end_time: datetime
    trip_id: int
    user_id: int
    bike_id: int


class BikeTripEndRequest(BaseModel):
    """BIke end trip parameters"""

    maintenance: bool = False
    ignore_zone: bool = False


class BikeTripStartRequest(BaseModel):
    """BIke start trip parameters"""

    user_id: int
    trip_id: int
