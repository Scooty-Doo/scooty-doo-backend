from fastapi import FastAPI

# from routes.bikes import router as bikes_router
from routes import bikes, trips, users, zones


app = FastAPI(
    title="Scooty Doo API",
    summary="Everything you need to make a custom app with the Scooty Doo API",
)

app.include_router(bikes.router)
app.include_router(zones.router)
app.include_router(users.router)
app.include_router(trips.router)


@app.get("/")
async def Welcome():
    return {"message": "Welcome to the Scooty Doo API!"}
