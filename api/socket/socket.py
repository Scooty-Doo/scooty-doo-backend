"""Module that creates socket"""

import socketio

socket = socketio.AsyncServer(cors_allowed_origins=[], async_mode="asgi")


async def emit_update(bike_id, updated_bike):
    """Emits updated bike data to socket."""
    # TODO: Pydantic model, maybe?
    print("Emitting")
    output_data = {
        "bike_id": bike_id,
        "last_position": updated_bike.last_position,
        "city_id": updated_bike.city_id,
        "battery_lvl": updated_bike.battery_lvl,
        "is_available": updated_bike.is_available,
        "meta_data": updated_bike.meta_data,
    }
    await socket.emit("bike_update", data=output_data, room="bike_updates")
    return
  