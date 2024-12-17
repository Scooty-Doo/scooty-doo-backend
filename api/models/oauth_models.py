"""MOdule with models for OAuth2"""

from pydantic import BaseModel


class GitHubCode(BaseModel):
    """Model for the GitHub OAuth2 code."""

    code: str
