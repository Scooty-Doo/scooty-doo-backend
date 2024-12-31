"""Exception handlers for the API."""

from typing import Union

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from api.models.models import JsonApiError, JsonApiErrorResponse


class ApiException(Exception):
    """Base exception for API errors."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    title: str = "Internal Server Error"

    def __init__(self, detail: str = None):
        self.detail = detail or self.title

    def __str__(self):
        return self.detail

class ZoneTypeNameExistsException(ApiException):
    """Exception raised when attempting to create zone type with existing name."""

    status_code = status.HTTP_409_CONFLICT
    title = "Zone Type Name Already Exists"

class ZoneTypeNotFoundException(ApiException):
    """Exception raised when a zone type is not found."""

    status_code = status.HTTP_404_NOT_FOUND
    title = "Zone Type Not Found"

class UserNotFoundException(ApiException):
    """Exception raised when a user is not found."""

    status_code = status.HTTP_404_NOT_FOUND
    title = "User Not Found"


class UserNotEligibleException(ApiException):
    """Exception raised when a user is not eligible."""

    status_code = status.HTTP_403_FORBIDDEN
    title = "User Not Eligible"


class UserEmailExistsException(ApiException):
    """Exception raised when attempting to create user with existing email."""

    status_code = status.HTTP_409_CONFLICT
    title = "Email Already Exists"


class ActiveTripExistsException(ApiException):
    """Exception raised when user already has an active trip."""

    status_code = status.HTTP_409_CONFLICT
    title = "Active Trip Exists"


class BikeRejectedError(ApiException):
    """Exception raised when bike rejects rental request."""

    status_code = status.HTTP_400_BAD_REQUEST
    title = "Bike Rental Rejected"


class BikeServiceUnavailableError(ApiException):
    """Exception raised when bike service cannot be reached."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    title = "Bike Service Unavailable"


class TripNotFoundException(ApiException):
    """Exception raised when a trip is not found."""

    status_code = status.HTTP_404_NOT_FOUND
    title = "Trip Not Found"


class UnauthorizedTripAccessException(ApiException):
    """Exception raised when a user tries to access a trip they do not own."""

    status_code = status.HTTP_403_FORBIDDEN
    title = "Unauthorized Trip Access"


class TripAlreadyEndedException(ApiException):
    """Exception raised when a trip has already ended."""

    status_code = status.HTTP_409_CONFLICT
    title = "Trip Already Ended"


async def api_exception_handler(
    request: Request,  # pylint: disable=unused-argument
    exc: ApiException,
) -> JSONResponse:
    """Handle API exceptions in JSON:API format."""
    return JSONResponse(
        status_code=exc.status_code,
        content=JsonApiErrorResponse(
            errors=[JsonApiError(status=str(exc.status_code), title=exc.title, detail=str(exc))]
        ).model_dump(),
    )


async def validation_exception_handler(
    request: Request,  # pylint: disable=unused-argument # noqa: ARG001
    exc: Union[RequestValidationError, ValidationError],
) -> JSONResponse:
    """Handle validation errors in JSON:API format. Request param required for FastAPI."""
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
