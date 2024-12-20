"""Application config module

pydantic_settings for type-safe configuration management.
Settings can be overridden using environment variables.
"""

from pydantic_settings import BaseSettings


# pylint: disable=too-few-public-methods
class Settings(BaseSettings):
    """Application settings.

    Attributes:
        project_name: Name of the project, used in API docs
        debug: Debug mode flag, enables detailed error responses
        environment: Current environment (local, dev, prod)
        database_url: PostgreSQL connection string

    Environment Variables:
        These settings can be overridden using env vars:
        - PROJECT_NAME: str
        - DEBUG: bool
        - ENVIRONMENT: str
        - DATABASE_URL: str (postgresql+asyncpg://user:pass@host:port/db)
    """

    project_name: str = "scooty-doo"
    debug: bool = False
    environment: str = "local"
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/sddb"
    github_client_id: str = "secretid"
    github_client_secret: str = "secret"
    github_redirect_uri: str = "sercret"

    class Config:
        """Pydantic model config.

        Specifies that settings should be loaded from .env file
        if it exists.
        """

        env_file = ".env"


# Create global settings instance
settings = Settings()
