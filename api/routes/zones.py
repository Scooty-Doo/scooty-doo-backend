"""Module for the /zones routes"""

from fastapi import APIRouter, status

router = APIRouter(
    prefix="/v1/zones",
    tags=["zones"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def get_zones(geofence):
    """Gets the zones in the perimiters of the geofence."""
    return {"zones": []}


@router.post("/")
def create_zone(zone):
    """Creates a zone."""
    return {zone}


@router.get("/{zone_id}")
def get_zone(zone_id):
    """Gets a zone."""
    return {zone_id}


@router.put("/{zone_id}")
def update_zone(zone_id):
    """Updates a zone."""
    return {zone_id}


@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_zone(zone_id):
    """Deletes a zone."""
    return {"Message": "Removed zone {zone_id}"}


# Used to get the parking zones. Query to filter.
@router.get("/parking")
def get_stations(query):
    """Gets the parking zones."""
    return {query}
