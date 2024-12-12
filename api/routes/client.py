"""Module for the /client routes."""

from db import db
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from models.output_models import BikeUser
from pydantic import Json

router = APIRouter(
    prefix="/v1/client",
    tags=["client"],
    responses={404: {"description": "Not found"}},
)


@router.get("/bikes")
async def get_all_bikes() -> Json[list[BikeUser]]:
    """Gets all available bikes in the current city
    from the database and returns in client format."""
    res = db.get_all_client_bikes()
    return JSONResponse(jsonable_encoder({"data": res}))


@router.get("/bikes/{bike_id}")
async def get_bike(bike_id: int) -> Json[BikeUser]:
    """Gets a bike from the database and returns in client format."""
    res = db.get_bike(bike_id)
    return JSONResponse(jsonable_encoder({"data": [res]}))
