# Fake db used to mock project structure
from datetime import datetime
from ..models.models import Bike
from ..models.models import City

current_time = datetime.now()
mocked_bikes = [    
    Bike(id=1, battery_level=100, metadata="So cool and red", position=[14.2089, 15.1092],
         city=City(id=1, city_name="Malmö", country_code="SWE", c_location="pos",
        created_at=current_time, updated_at=current_time),
         status="Available", created_at=current_time, updated_at=current_time),
    Bike(id=2, battery_level=12, metadata="Sad and blue", position=[11.2089, 14.1092],
         city=City(id=2, city_name="Göteborg", country_code="SWE", c_location="pos",
        created_at=current_time, updated_at=current_time),
         status="Under maintenance", created_at=current_time, updated_at=current_time),
]


def get_all_bikes() -> list[Bike]:
    return mocked_bikes


def get_bike(bike_id: int) -> Bike:
    for bike in mocked_bikes:
        if bike.id == bike_id:
            return bike
    return None


def add_bike(bike):
    try:
        mocked_bikes.update({bike})
        return bike
    except:
        return "Ruh roh!"


def remove_bike(bike_id: int):
    for index, bike in enumerate(mocked_bikes):
        if bike.id == bike_id:
            mocked_bikes.pop(index)
            return "Bike removed"
    raise KeyError


def update_bike(bike_data: Bike):
    for bike in mocked_bikes:
        if bike.id == bike_data.id:
            bike = bike_data # Maybe some checks if fields are empty
            return bike
    raise KeyError
