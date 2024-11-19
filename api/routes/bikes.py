from fastapi import APIRouter, HTTPException, status
from db import db
from pydantic import BaseModel

# Change depending on ORM/Database
class Bike(BaseModel):
    bike_id: int
    position: list[int]
    status: str
    in_use: bool


router = APIRouter(
    prefix="/v1/bikes",
    tags=["bikes"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_all_bikes():
    res = db.get_all_bikes()
    return res

@router.get("/{bike_id}")
async def get_bike(bike_id: int):
    res = db.get_bike(bike_id)
    return res

@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_bike(bike: Bike):
    try:
        db.add_bike(bike)
        return bike
    except:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{bike_id}")
async def update_bike(bike: Bike):
    try:
        db.update_bike(bike)
        return bike
    except:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{bike_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_bike(bike_id: int):
    try:
        db.remove_bike(bike_id)
        return 
    except:
        raise HTTPException(status_code=500, detail="Internal server error")
    