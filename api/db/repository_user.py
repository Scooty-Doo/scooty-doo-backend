"""Repository module for database operations."""

from typing import Any, Optional

from sqlalchemy import BinaryExpression, and_, asc, desc, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from api.db.repository_base import DatabaseRepository
from api.exceptions import (
    UserGithubLoginExistsException,
    UserNotEligibleException,
    UserNotFoundException,
)
from api.models import db_models


class UserRepository(DatabaseRepository[db_models.User]):
    """Repository for trip-specific operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with the Trip model."""
        super().__init__(db_models.User, session)

    async def check_user_eligibility(self, user_id: int) -> None:
        """Check if a user exists, and if they have prepay check that they have positive balance.
        TODO: Check if user allready has trips ongoing"""
        user = await self.get(user_id)
        if user is None:
            raise UserNotFoundException(f"User with ID {user_id} not found.")
        if user.use_prepay and user.balance <= 0:
            raise UserNotEligibleException(
                f"User with ID {user_id} is not eligible due to insufficient balance."
            )

    async def get_user_id_from_github_login(self, github_login: str) -> int:
        """Get user ID by GitHub login.

        Returns:
            UserId: Model containing user ID
        Raises:
            UserNotFoundException: If user not found
        """
        stmt = select(self.model.id).where(self.model.github_login == github_login)
        result = await self.session.execute(stmt)
        user_id = result.scalar_one_or_none()

        if user_id is None:
            raise UserNotFoundException(f"User with GitHub login {github_login} not found.")

        return user_id

    def _build_filters(self, **params: dict[str, Any]) -> list[BinaryExpression]:
        """Filter builder for user queries."""
        filter_map = {
            "name_search": lambda v: self.model.full_name.ilike(f"%{v}%"),
            "email_search": lambda v: self.model.email.ilike(f"%{v}%"),
            "github_login_search": lambda v: self.model.github_login.ilike(f"%{v}%"),
            "balance_gt": lambda v: self.model.balance > v,
            "balance_lt": lambda v: self.model.balance < v,
            "created_at_gt": lambda v: self.model.created_at > v,
            "created_at_lt": lambda v: self.model.created_at < v,
            "updated_at_gt": lambda v: self.model.updated_at > v,
            "updated_at_lt": lambda v: self.model.updated_at < v,
        }

        return [
            filter_map[key](value)
            for key, value in params.items()
            if key in filter_map and value is not None
        ]

    async def get_users(self, **params) -> list[db_models.User]:
        """Get all users without their relationships, applying filters, sorting, and pagination."""
        stmt = select(self.model)

        filters = self._build_filters(**params)
        if filters:
            stmt = stmt.where(and_(*filters))

        order_column = getattr(self.model, params.get("order_by", "created_at"))
        stmt = stmt.order_by(
            desc(order_column) if params.get("order_direction") == "desc" else asc(order_column)
        )

        stmt = stmt.offset(params.get("offset", 0)).limit(params.get("limit", 100))

        result = await self.session.execute(stmt)
        users = list(result.unique().scalars())

        return users

    async def get_user(self, user_id: int) -> db_models.User:
        """Get a user by ID with relationships eagerly loaded."""
        stmt = (
            select(self.model)
            .options(
                selectinload(self.model.payment_methods),
                selectinload(self.model.trips),
                selectinload(self.model.transactions),
            )
            .where(self.model.id == user_id)
        )

        result = await self.session.execute(stmt)
        user = result.unique().scalar_one_or_none()

        if user is None:
            raise UserNotFoundException(f"User with ID {user_id} not found.")

        return user

    async def create_user(self, user_data: dict[str, Any]) -> db_models.User:
        """Create a new user."""
        try:
            user = db_models.User(**user_data)
            self.session.add(user)
            await self.session.commit()

            await self.session.refresh(user)
            return user
        except IntegrityError as e:
            await self.session.rollback()
            if "users_github_login_key" in str(e):
                raise UserGithubLoginExistsException(
                    f"User with GitHub username {user_data['github_login']} already exists."
                ) from e
            raise

    async def update_user(self, user_id: int, data: dict[str, Any]) -> Optional[db_models.User]:
        """Update a user by primary key."""
        try:
            # Update user
            update_stmt = (
                update(self.model)
                .where(self.model.id == user_id)
                .values(**data)
                .returning(self.model.id)
            )

            result = await self.session.execute(update_stmt)
            if not result.scalar_one_or_none():
                raise UserNotFoundException(f"User with ID {user_id} not found.")

            # Get updated user with relationships
            select_stmt = (
                select(self.model)
                .options(
                    joinedload(self.model.payment_methods),
                    joinedload(self.model.trips),
                    joinedload(self.model.transactions),
                )
                .where(self.model.id == user_id)
            )

            result = await self.session.execute(select_stmt)
            await self.session.commit()
            return result.unique().scalar_one()

        except IntegrityError as e:
            await self.session.rollback()
            if "users_github_login_key" in str(e):
                raise UserGithubLoginExistsException(
                    f"User with GitHub username {data.get('github_login')} already exists."
                ) from e
            raise
