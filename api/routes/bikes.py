from pydantic import Json
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from ..models import db_models as db_models
from ..db import db
from ..models.models import Bike

from ..models.bike_test import BikeTest
from typing import Annotated
from ..db import repository
# from database.repository import BikeRepository
from api.dependencies.dependencies import get_repository

router = APIRouter(
    prefix="/v1/bikes",
    tags=["bikes"],
    responses={404: {"description": "Not found"}},
)

BikeRepository = Annotated[repository.DatabaseRepository[db_models.Bike], Depends(get_repository(db_models.Bike))]

@router.get("/available", response_model=list[BikeTest])
async def get_available_bikes(
    repository: BikeRepository
) -> list[BikeTest]:
    bikes = await repository.filter(db_models.Bike.is_available)
    return [BikeTest.model_validate(bike) for bike in bikes]

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
