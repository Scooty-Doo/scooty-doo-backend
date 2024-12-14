"""Module for the /trips routes"""

from fastapi import APIRouter, status

router = APIRouter(
    prefix="/v1/trips",
    tags=["trips"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def get_trips():
    """Gets all trips from the database."""
    return {"trips": []}


@router.post("/")
def start_trip(trip):
    """Starts a trip."""
    return {trip}


@router.get("/{trip_id}")
def get_trip(trip_id):
    """Gets a trip from the database."""
    return {trip_id}


# Used for stopping trips
@router.put("/{trip_id}")
def update_trip(trip_id):
    """Updates a trip."""
    return {trip_id}


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_trip(trip_id):
    """Removes a trip from the database."""
    return {"Message": "Removed trip {trip_id}"}


# Used for getting the trips that a specific bike has been used on
@router.get("/bike/{bike_id}")
def get_trips_for_bike(bike_id):
    """Gets all trips for a specific biek from the database."""
    return {bike_id}


# Used for getting a specific trip on a specific bike
@router.get("/bike/{bike_d}/trip/{trip_id}")
def get_trip_for_bike(bike_id, trip_id):
    """Gets getting a specific trip on a specific bike from the database."""
    return {"trip": trip_id, "bike": bike_id}


# Used to get a users trip history
@router.get("/user/{user_id}")
def get_user_history(user_id):
    """Gets a users trip history."""
    return {user_id}
