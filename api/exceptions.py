"""Exception handlers for the API."""

from typing import Union

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from api.models.models import JsonApiError, JsonApiErrorResponse


async def validation_exception_handler(
    request: Request, exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """Handle validation errors in JSON:API format."""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")

        errors.append(
            JsonApiError(
                status="422",
                title="Validation Error",
                detail=f"{field}: {error['msg']}" if field else error["msg"],
            )
        )

    return JSONResponse(
        status_code=422,
        content=JsonApiErrorResponse(errors=errors).model_dump(),
    )
