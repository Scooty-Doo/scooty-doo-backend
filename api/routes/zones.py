from fastapi import APIRouter, status

router = APIRouter(
    prefix="/v1/zones",
    tags=["zones"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def get_zones(geofence):
    return {"zones": []}


@router.post("/")
def create_zone(zone):
    return {zone}


@router.get("/{id}")
def get_zone(id):
    return {id}


@router.put("/{id}")
def update_zone(id):
    return {id}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_zone(id):
    return {"Message": "Removed zone {id}"}


# Used to get the parking zones. Query to filter.
@router.get("/parking")
def get_stations(query):
    return {query}
