import datetime

from api.models.db_models import Bike, Trip, User

fake_bike_data = [
    Bike(
        id=1,
        battery_lvl=45,
        city_id=1,
        last_position="POINT(13.06782 55.577859)",
        is_available=False,
        meta_data=None,
        created_at=datetime.datetime(2024, 7, 13, 7, 56, 50, 758246, tzinfo=datetime.timezone.utc),
        updated_at=datetime.datetime(
            2024, 12, 17, 14, 21, 44, 610901, tzinfo=datetime.timezone.utc
        ),
    ),
    Bike(
        id=2,
        battery_lvl=95,
        city_id=3,
        is_available=True,
        meta_data=None,
        created_at=datetime.datetime(2024, 7, 13, 7, 56, 51, 758246, tzinfo=datetime.timezone.utc),
        updated_at=datetime.datetime(
            2024, 12, 17, 14, 21, 46, 610901, tzinfo=datetime.timezone.utc
        ),
    ),
]

fake_user_data = User(id=652134919185249719)

fake_trip = Trip(
    id=12409712904,
    start_position="POINT(13.05 55.23)",
    start_time=datetime.datetime(2024, 7, 13, 7, 56, 51, 758246),
    created_at=datetime.datetime(2024, 7, 13, 7, 56, 51, 758246, tzinfo=datetime.timezone.utc),
    updated_at=datetime.datetime(2024, 12, 17, 14, 21, 46, 610901, tzinfo=datetime.timezone.utc),
)
