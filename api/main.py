from db import db
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def Welcome():
    return {"message": "Welcome to the Scooty Doo API!"}

@app.get("/bikes")
async def get_all_bikes():
    res = db.get_all_bikes()

    return res

@app.get("/bikes/{bike_id}")
async def get_bike(bike_id: int):
    return {"bike_id": bike_id}
