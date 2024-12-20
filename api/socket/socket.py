"""Module that creates socket"""

import socketio

socket = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
