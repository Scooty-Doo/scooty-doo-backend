"""Module that creates socket"""

import socketio

from api.models.bike_models import BikeSocket, BikeSocketStartEnd

socket = socketio.AsyncServer(cors_allowed_origins=[], async_mode="asgi")


async def emit_update(updated_bike: BikeSocket):
    """Emits updated bike data to socket."""
    await socket.emit("bike_update", data=updated_bike, room="bike_updates")


async def emit_update_start_end(updated_bike: BikeSocketStartEnd, start_or_end: str):
    """Emits updated bike data to socket."""
    await socket.emit(start_or_end, data=updated_bike, room="bike_updates")
