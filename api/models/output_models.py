"""Module for the output data models"""

import datetime

from pydantic import BaseModel, Field

from .models import City


class BikeUser(BaseModel):
    """Output model for bike table for users"""

    id: int
    battery_level: int
    position: str = Field(pattern=r"POINT\(\d{2}\.\d{4}\s\d{2}\.\d{4}\)")


class BikeAdmin(BaseModel):
    """Output model for bike table for admins"""

    id: int
    battery_level: int
    metadata: str
    position: str = Field(pattern=r"POINT\(\d{2}\.\d{4}\s\d{2}\.\d{4}\)")
    city_id: int
    city_name: str
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    @classmethod
    def from_city(cls, bike_data: dict, city: City):
        """Gets city id field and city name field from city model"""
        bike_data["city_id"] = city.id
        bike_data["city_name"] = city.city_name
        return cls(**bike_data)
