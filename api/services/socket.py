"""Module that creates socket"""

import socketio

from api.models.bike_models import BikeSocket

socket = socketio.AsyncServer(cors_allowed_origins=[], async_mode="asgi")


async def emit_update(updated_bike: BikeSocket):
    """Emits updated bike data to socket."""
    await socket.emit("bike_update", data=updated_bike.model_dump(), room="bike_updates")
