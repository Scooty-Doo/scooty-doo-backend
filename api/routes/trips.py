from fastapi import APIRouter, status

router = APIRouter(
    prefix="/v1/trips",
    tags=["trips"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def get_trips():
    return {"trips": []}


@router.post("/")
def start_trip(trip):
    return {trip}


@router.get("/{id}")
def get_trip(id):
    return {id}


# Used for stopping trips
@router.put("/{id}")
def update_trip(id):
    return {id}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_trip(id):
    return {"Message": "Removed trip {id}"}


# Used for getting the trips that a specific bike has been used on
@router.get("/bike/{id}")
def get_trips_for_bike(id):
    return {id}


# Used for getting a specific trip on a specific bike
@router.get("/bike/{id}/trip/{trip_id}")
def get_trip_for_bike(id, trip_id):
    return {"trip": trip_id, "bike": id}


# Used to get a users trip history
@router.get("/user/{id}")
def get_user_history(id):
    return {id}
