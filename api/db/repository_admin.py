"""Repository module for database operations."""

from typing import Any

from sqlalchemy import BinaryExpression, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.repository_base import DatabaseRepository
from api.exceptions import (
    UserNotFoundException,
)
from api.models import db_models


class AdminRepository(DatabaseRepository[db_models.Admin]):
    """Repository for admin operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with the Admin model."""
        super().__init__(db_models.Admin, session)

    async def get_admin_id_from_github_login(self, github_login: str) -> int:
        """Get admin ID by GitHub login.

        Returns:
            AdminId: Model containing admin ID
        Raises:
            UserNotFoundException: If admin not found
        """
        stmt = select(self.model.id).where(self.model.github_login == github_login)
        result = await self.session.execute(stmt)
        admin_id = result.scalar_one_or_none()

        if admin_id is None:
            raise UserNotFoundException(f"User with GitHub login {github_login} not found.")

        return admin_id

    def _build_filters(self, **params: dict[str, Any]) -> list[BinaryExpression]:
        """Filter builder for admin queries."""
        filter_map = {
            "name_search": lambda v: self.model.full_name.ilike(f"%{v}%"),
            "email_search": lambda v: self.model.email.ilike(f"%{v}%"),
            "github_login_search": lambda v: self.model.github_login.ilike(f"%{v}%"),
        }

        return [
            filter_map[key](value)
            for key, value in params.items()
            if key in filter_map and value is not None
        ]

    async def get_admin(self, admin_id: int) -> db_models.Admin:
        """Get a admin by ID."""
        stmt = select(self.model).where(self.model.id == admin_id)

        result = await self.session.execute(stmt)
        admin = result.unique().scalar_one_or_none()

        if admin is None:
            raise UserNotFoundException(f"Admin with ID {admin_id} not found.")

        return admin

    async def get_admins(self, **params: dict[str, Any]) -> list[db_models.Admin]:
        """Get a list of admins."""
        stmt = select(self.model).filter(*self._build_filters(**params))

        result = await self.session.execute(stmt)
        admins = result.scalars().all()

        return admins
