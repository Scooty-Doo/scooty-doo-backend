"""Repository module for database operations."""

import re
from typing import Any, Optional

from geoalchemy2.functions import ST_AsText
from geoalchemy2.shape import to_shape
from sqlalchemy import BinaryExpression, and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.repository_base import DatabaseRepository
from api.models import db_models


class UserRepository(DatabaseRepository[db_models.User]):
    """Repository for trip-specific operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with the Trip model."""
        super().__init__(db_models.User, session)
