"""Main API file used to start server."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from api.db.database import sessionmanager
from api.exceptions import validation_exception_handler
from api.routes import bikes, oauth, trips, users, zones

sessionmanager.init("postgresql+asyncpg://user:pass@localhost:5432/sddb")


@asynccontextmanager
async def lifespan(application: FastAPI):  # pylint: disable=unused-argument
    """Context manager for the lifespan of the application."""
    yield
    if sessionmanager.is_initialized:
        await sessionmanager.close()


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
app.include_router(oauth.router)

# Add exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)


@app.get("/")
async def welcome():
    """Sends a message for root path."""
    return {"message": "Welcome to the Scooty Doo API!"}
