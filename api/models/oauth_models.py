"""MOdule with models for OAuth2"""

from typing import Optional

from pydantic import BaseModel

from api.models.user_models import UserCreate


class GitHubCode(BaseModel):
    """Model for the GitHub OAuth2 code."""

    code: str


class UserId(BaseModel):
    """Model for the user id."""

    id: int


class GitHubUserResponse(BaseModel):
    """GitHub API user response model"""

    login: str
    name: Optional[str] = None
    email: Optional[str] = None

    def to_user_create(self) -> UserCreate:
        """Convert GitHub response to UserCreate model"""
        return UserCreate(
            full_name=self.name,
            email=self.email,
            github_login=self.login,
        )
