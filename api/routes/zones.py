"""Module for the /zones routes"""

from fastapi import APIRouter

router = APIRouter(
    prefix="/v1/zones",
    tags=["zones"],
    responses={404: {"description": "Not found"}},
)
