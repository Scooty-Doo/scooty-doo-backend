"""Module with pydantic admin models"""

# pylint: disable=too-few-public-methods
from datetime import datetime
from typing import Annotated, Any, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from api.models.models import JsonApiLinks

GitHubUsername = Annotated[
    str,
    Field(..., min_length=1, max_length=39, pattern=r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?$"),
]


class AdminAttributes(BaseModel):
    """User attributes for JSON:API response."""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    github_login: GitHubUsername
    meta_data: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminResource(BaseModel):
    """JSON:API resource object for Admins."""

    id: str
    type: str = "admins"
    attributes: AdminAttributes
    links: Optional[JsonApiLinks] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_db_model(cls, admin: Any) -> "AdminResource":
        """Create a AdminResource from a database model."""
        return cls(
            id=str(admin.id),
            attributes=AdminAttributes.model_validate(admin),
            # links=JsonApiLinks(self_link=f"{request_url}"),
        )


class AdminGetRequestParams(BaseModel):
    """Model for getting a admin"""

    name_search: Optional[str] = Field(None, min_length=3)
    email_search: Optional[str] = Field(None, min_length=3)
    github_login_search: Optional[GitHubUsername] = None
