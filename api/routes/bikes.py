from pydantic import Json
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from db import db
from models.models import Bike

router = APIRouter(
    prefix="/v1/bikes",
    tags=["bikes"],
    responses={404: {"description": "Not found"}},
)


# Include geographical filter
@router.get("/")
async def get_all_bikes() -> Json[list[Bike]]:
    res = db.get_all_bikes()
    return JSONResponse(jsonable_encoder({'data': res}))


@router.get("/{bike_id}")
async def get_bike(bike_id: int) -> Json[Bike]:
    res = db.get_bike(bike_id)
    return JSONResponse(jsonable_encoder({'data': [res]}))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_bike(bike: Bike) -> Json[Bike]:
    try:
        new_bike = db.add_bike(bike)
        return JSONResponse(jsonable_encoder({"message": "New bike added", 'data': [new_bike]}))
    except ValueError:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{bike_id}")
async def update_bike(bike: Bike) -> Json[Bike]:
    try:
        updated_bike = db.update_bike(bike)
        return JSONResponse(jsonable_encoder({'data': [updated_bike]}))
    except ValueError:
        raise HTTPException(status_code=500, detail="Internal server error")
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No bike found")


@router.delete("/{bike_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_bike(bike_id: int) -> None:
    try:
        db.remove_bike(bike_id)
        return
    except ValueError:
        raise HTTPException(status_code=500, detail="Internal server error")
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No bike found")
