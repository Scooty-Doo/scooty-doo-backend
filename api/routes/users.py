from fastapi import APIRouter

router = APIRouter(
    prefix="/v1/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
def get_users():
    return {"users": []}
