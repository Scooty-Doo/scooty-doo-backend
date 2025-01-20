"""Main API file used to start server."""

from contextlib import asynccontextmanager

import socketio
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from api.config import settings
from api.db.database import sessionmanager
from api.exceptions import (
    ApiException,
    api_exception_handler,
    validation_exception_handler,
)
from api.routes import admin, bikes, cities, me, oauth, stripe, transactions, trips, users, zones
from api.routes.dev_routes import admin as dev_admin, bikes as dev_bikes, cities as dev_cities, me as dev_me, oauth as dev_oauth, stripe as dev_stripe, transactions as dev_transactions, trips as dev_trips, users as dev_users, zones as dev_zones
from api.services.socket import socket

sessionmanager.init(settings.database_url)


@asynccontextmanager
async def lifespan(application: FastAPI):  # pylint: disable=unused-argument
    """Context manager for the lifespan of the application."""
    yield
    if sessionmanager.is_initialized:
        await sessionmanager.close()

v1_app = FastAPI(
    title="Scooty Doo API v1",
    openapi_prefix="/v1",
    openapi_tags=[{"name": "v1"}]
)

dev_app = FastAPI(
    title="Scooty Doo API Dev",
    openapi_prefix="/dev",
    openapi_tags=[{"name": "dev"}]
)

app = FastAPI(
    title="Scooty Doo API",
    root_path="/",
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

v1_app.include_router(bikes.router)
v1_app.include_router(zones.router)
v1_app.include_router(users.router)
v1_app.include_router(trips.router)
v1_app.include_router(oauth.router)
v1_app.include_router(transactions.router)
v1_app.include_router(stripe.router)
v1_app.include_router(me.router)
v1_app.include_router(admin.router)
v1_app.include_router(cities.router)

dev_app.include_router(dev_bikes.router)
dev_app.include_router(dev_zones.router)
dev_app.include_router(dev_users.router)
dev_app.include_router(dev_trips.router)
dev_app.include_router(dev_oauth.router)
dev_app.include_router(dev_transactions.router)
dev_app.include_router(dev_stripe.router)
dev_app.include_router(dev_me.router)
dev_app.include_router(dev_admin.router)
dev_app.include_router(dev_cities.router)

app.mount("/v1", v1_app)
app.mount("/dev", dev_app)

# Add exception handlers
app.add_exception_handler(ApiException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)


@app.get("/")
async def welcome():
    """Sends a message for root path."""
    return {"message": "Welcome to the Scooty Doo API!"}


socket_app = socketio.ASGIApp(socket)

app.mount("/", socket_app)


@socket.event
async def connect(sid: int, _):
    """Function for when client connects to socket."""
    await socket.enter_room(sid, "bike_updates")
