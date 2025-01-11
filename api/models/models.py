"""Module for pydantic models
Note: JSON:API integration with FastAPI feels clunky.
use a library like fastapi-jsonapi?
https://fastapi-jsonapi.readthedocs.io/en/latest/
"""

# pylint: disable=too-few-public-methods
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class JsonApiLinks(BaseModel):
    """JSON:API links object."""

    self_link: str = Field(..., alias="self")

    model_config = ConfigDict(populate_by_name=True)


class JsonApiError(BaseModel):
    """JSON:API error object."""

    status: str
    title: str
    detail: Optional[str] = None


class JsonApiErrorResponse(BaseModel):
    """JSON:API error response."""

    errors: list[JsonApiError]


T = TypeVar("T", bound=BaseModel)


class JsonApiResponse(BaseModel, Generic[T]):
    """JSON:API response wrapper."""

    data: T | list[T]
    links: JsonApiLinks
