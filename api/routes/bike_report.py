from fastapi import APIRouter

router = APIRouter(
    prefix="/v1/bike_report",
    tags=["bike_report"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def server_ping():
    return {"Pong"}


# Used when bike reports status
@router.put("/status/{id}")
def bike_report_status(id, data):
    return {id: data}
