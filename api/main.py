"""Main API file used to start server."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import bikes, trips, users, zones

app = FastAPI(
    title="Scooty Doo API",
    summary="Everything you need to make a custom app with the Scooty Doo API",
)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://localhost",
    "https://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bikes.router)
app.include_router(zones.router)
app.include_router(users.router)
app.include_router(trips.router)


@app.get("/")
async def welcome():
    """Sends a message for root path."""
    return {"message": "Welcome to the Scooty Doo API!"}
