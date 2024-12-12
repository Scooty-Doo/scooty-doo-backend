"""Fake db used to mock project structure"""

from datetime import datetime

from models.models import Bike, City

current_time = datetime.now()
mocked_bikes = [
    Bike(
        id=1,
        battery_level=100,
        metadata="So cool and red",
        position="POINT(13.0038 55.6050)",
        city=City(
            id=1,
            city_name="Malmö",
            country_code="SWE",
            c_location="POINT(13.0038 55.6050)",
            created_at=current_time,
            updated_at=current_time,
        ),
        status="Available",
        created_at=current_time,
        updated_at=current_time,
    ),
    Bike(
        id=2,
        battery_level=12,
        metadata="Sad and blue",
        position="POINT(13.0038 55.6050)",
        city=City(
            id=2,
            city_name="Göteborg",
            country_code="SWE",
            c_location="pos",
            created_at=current_time,
            updated_at=current_time,
        ),
        status="Under maintenance",
        created_at=current_time,
        updated_at=current_time,
    ),
]


def get_all_bikes() -> list[Bike]:
    """Gets all bikes from mocked data."""
    return mocked_bikes


def get_bike(bike_id: int) -> Bike:
    """Gets a single bike by id from mocked data."""
    for bike in mocked_bikes:
        if bike.id == bike_id:
            return bike
    return None


def add_bike(bike):
    """Adds a bike to the mocked data."""
    try:
        mocked_bikes.append({bike})
        return bike
    except ValueError:
        return "Ruh roh!"


def remove_bike(bike_id: int):
    """Removes a bike from the mocked data."""
    for index, bike in enumerate(mocked_bikes):
        if bike.id == bike_id:
            mocked_bikes.pop(index)
            return "Bike removed"
    raise KeyError


def update_bike(bike_data: Bike):
    """Updates a bike."""
    for bike in mocked_bikes:
        if bike.id == bike_data.id:
            bike = bike_data  # Maybe some checks if fields are empty
            return bike
    raise KeyError


def get_all_client_bikes():
    """Gets bikes with mininal info for client"""
    return mocked_bikes
