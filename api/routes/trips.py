from fastapi import APIRouter

router = APIRouter(
    prefix="/v1/trips",
    tags=["trips"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
def get_trips():
    return {"trips": []}
