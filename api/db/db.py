# Fake db used to mock project structure


def get_all_bikes():
    return {"bikes": [{"bike_id": 1}, {"bike_id": 2}]}


def get_bike(bike_id: int):
    return {"bike_id": 1, "bike_status": "ok"}


def add_bike(bike):
    return bike


def remove_bike(bike_id: int):
    return ""


def update_bike(bike):
    return bike
