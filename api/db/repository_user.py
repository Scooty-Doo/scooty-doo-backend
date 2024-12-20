"""Repository module for database operations."""

import re
from typing import Any, Optional

from geoalchemy2.functions import ST_AsText
from geoalchemy2.shape import to_shape
from sqlalchemy import BinaryExpression, and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.repository_base import DatabaseRepository
from api.models import db_models
from api.exceptions import UserNotFoundException, UserNotEligibleException


class UserRepository(DatabaseRepository[db_models.User]):
    """Repository for trip-specific operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with the Trip model."""
        super().__init__(db_models.User, session)


    async def check_user_eligibility(self, user_id: int) -> None:
        """Check if a user exists, and if they have prepay check that they have positive balance."""
        user = await self.get(user_id)
        if user is None:
            raise UserNotFoundException(f"User with ID {user_id} not found.")
        if user.use_prepay and user.balance <= 0:
            raise UserNotEligibleException(f"User with ID {user_id} is not eligible due to insufficient balance.")
