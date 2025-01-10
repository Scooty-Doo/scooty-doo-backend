"""Models for bikes"""

from typing import Optional

from pydantic import Field, field_validator

from api.models.models import BikeUpdate


class BikeSocket(BikeUpdate):
    """Socket output model"""

    bike_id: int
    zone_id: Optional[int] = Field(alias="end_map_zone_id", default=None)
    zone_type: Optional[str] = Field(alias="end_map_zone_type", default=None)

    @field_validator("battery_lvl", mode="before")
    @classmethod
    def cast_float_to_int(cls, value: float) -> int:
        """Casts battery_lvl to int"""
        return int(value)
