"""Module for the /bikes routes"""

from db import db
from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from models.models import Bike
from models.output_models import BikeAdmin
from pydantic import Json

router = APIRouter(
    prefix="/v1/bikes",
    tags=["bikes"],
    responses={404: {"description": "Not found"}},
)


# Include geographical filter => City!!!
@router.get("/")
async def get_all_bikes() -> Json[list[BikeAdmin]]:
    """Gets all bikes from the database and returns in admin format."""
    # Vem kollar GPS data för att veta vilken stad?
    res = db.get_all_bikes()
    return JSONResponse(jsonable_encoder({"data": res}))


@router.get("/{bike_id}")
async def get_bike(bike_id: int) -> Json[BikeAdmin]:
    """Gets one bike from the database and returns in admin format."""
    res = db.get_bike(bike_id)
    return JSONResponse(jsonable_encoder({"data": [res]}))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_bike(bike: Bike) -> Json[BikeAdmin]:
    """Adds a bike to the database."""
    try:
        new_bike = db.add_bike(bike)  # Kanske returnera id och sen hänmta i admin-format?
        return JSONResponse(jsonable_encoder({"message": "New bike added", "data": [new_bike]}))
    except ValueError:
        raise HTTPException(status_code=500, detail="Internal server error") from ValueError


@router.put("/{bike_id}")
async def update_bike(bike: BikeAdmin) -> Json[BikeAdmin]:
    """Updates a bike in the database and returns in admin format"""
    try:
        updated_bike = db.update_bike(bike)
        return JSONResponse(jsonable_encoder({"data": [updated_bike]}))
    except ValueError:
        raise HTTPException(status_code=500, detail="Internal server error") from ValueError
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No bike found"
        ) from KeyError


@router.delete("/{bike_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_bike(bike_id: int) -> None:
    """Removes a bike from the database."""
    try:
        db.remove_bike(bike_id)
        return
    except ValueError:
        raise HTTPException(status_code=500, detail="Internal server error") from ValueError
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No bike found"
        ) from KeyError
