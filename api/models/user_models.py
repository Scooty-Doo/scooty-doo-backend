"""Module with pydantic user models"""

# pylint: disable=too-few-public-methods
from datetime import datetime
from typing import Annotated, Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from api.models.models import JsonApiLinks

GitHubUsername = Annotated[
    str,
    Field(..., min_length=1, max_length=39, pattern=r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?$"),
]


class UserAttributes(BaseModel):
    """User attributes for JSON:API response."""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    github_login: GitHubUsername
    balance: Optional[float] = 0.00
    use_prepay: bool = False
    meta_data: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UserRelationships(BaseModel):
    """User relationships for JSON:API response."""

    payment_methods: Optional[dict[str, Any]] = None
    trips: Optional[dict[str, Any]] = None
    transactions: Optional[dict[str, Any]] = None

    model_config = ConfigDict(populate_by_name=True)


class UserResourceMinimal(BaseModel):
    """JSON:API resource object for users without relationships."""

    id: str
    type: str = "users"
    attributes: UserAttributes
    links: Optional[JsonApiLinks] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_db_model(cls, user: Any, request_url: str) -> "UserResourceMinimal":
        """Create a minimal UserResource from a database model."""
        return cls(
            id=str(user.id),
            attributes=UserAttributes.model_validate(user),
            links=JsonApiLinks(self_link=f"{request_url}"),
        )


class UserResource(BaseModel):
    """JSON:API resource object for users."""

    id: str
    type: str = "users"
    attributes: UserAttributes
    relationships: Optional[UserRelationships] = None
    links: Optional[JsonApiLinks] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_db_model(cls, user: Any, request_url: str) -> "UserResource":
        """Create a UserResource from a database model."""
        relationships = {}

        if hasattr(user, "payment_methods") and user.payment_methods is not None:
            relationships["payment_methods"] = {
                "data": [
                    {"type": "payment_methods", "id": str(pm.id)} for pm in user.payment_methods
                ]
            }

        if hasattr(user, "trips") and user.trips is not None:
            relationships["trips"] = {
                "data": [{"type": "trips", "id": str(trip.id)} for trip in user.trips]
            }

        if hasattr(user, "transactions") and user.transactions is not None:
            relationships["transactions"] = {
                "data": [{"type": "transactions", "id": str(txn.id)} for txn in user.transactions]
            }

        return cls(
            id=str(user.id),
            attributes=UserAttributes.model_validate(user),
            relationships=UserRelationships(**relationships) if relationships else None,
            links=JsonApiLinks(self_link=f"{request_url}"),
        )


class UserGetRequestParams(BaseModel):
    """Model for getting a user"""

    # Pagination defaults to 100 users per page
    limit: Optional[int] = Field(None, gt=0)
    offset: int = Field(0, ge=0)

    # Sorting
    order_by: Literal["created_at", "updated_at", "full_name", "email", "balance"] = "created_at"
    order_direction: Literal["asc", "desc"] = "desc"

    name_search: Optional[str] = Field(None, min_length=3)
    email_search: Optional[str] = Field(None, min_length=3)
    github_login_search: Optional[GitHubUsername] = None
    balance_gt: Optional[float] = None
    balance_lt: Optional[float] = None
    created_at_gt: Optional[datetime] = None
    created_at_lt: Optional[datetime] = None
    updated_at_gt: Optional[datetime] = None
    updated_at_lt: Optional[datetime] = None


class UserCreate(BaseModel):
    """Model for payload to create a user"""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    use_prepay: Optional[bool] = False
    github_login: GitHubUsername
    meta_data: Optional[dict] = None


class UserUpdate(BaseModel):
    """Model for updating a user"""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    github_login: Optional[GitHubUsername] = None
    use_prepay: Optional[bool] = None
    meta_data: Optional[dict] = None
