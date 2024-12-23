"""Repository module for database operations."""

import re
from typing import Any, Optional

from geoalchemy2.functions import ST_AsText
from geoalchemy2.shape import to_shape
from sqlalchemy import BinaryExpression, and_, select, update, desc, asc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.repository_base import DatabaseRepository
from api.models import db_models
from api.exceptions import UserNotFoundException, UserNotEligibleException, UserEmailExistsException
from api.models.user_models import UserCreate


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
            raise UserNotEligibleException(f"User with ID {user_id} is not eligible due to insufficient balance.")
    
    def _build_filters(self, **params: dict[str, Any]) -> list[BinaryExpression]:
        """Filter builder for user queries."""
        filter_map = {
            'name_search': lambda v: self.model.full_name.ilike(f"%{v}%"),
            'email_search': lambda v: self.model.email.ilike(f"%{v}%"),
            'balance_gt': lambda v: self.model.balance > v,
            'balance_lt': lambda v: self.model.balance < v,
            'created_at_gt': lambda v: self.model.created_at > v,
            'created_at_lt': lambda v: self.model.created_at < v,
            'updated_at_gt': lambda v: self.model.updated_at > v,
            'updated_at_lt': lambda v: self.model.updated_at < v,
        }
        
        return [
            filter_map[key](value)
            for key, value in params.items()
            if key in filter_map and value is not None
        ]

    async def get_users(self, **params) -> list[db_models.User]:
        """Get all users with their relationships, applying filters, sorting, and pagination."""
        stmt = select(self.model).options(
            joinedload(self.model.payment_methods),
            joinedload(self.model.trips),
            joinedload(self.model.transactions)
        )
        
        # Apply filters
        filters = self._build_filters(**params)
        if filters:
            stmt = stmt.where(and_(*filters))
            
        # Apply sorting
        order_column = getattr(self.model, params.get('order_by', 'created_at'))
        stmt = stmt.order_by(
            desc(order_column) if params.get('order_direction') == 'desc'
            else asc(order_column)
        )
        
        # Apply pagination
        stmt = stmt.offset(params.get('offset', 0)).limit(params.get('limit', 100))
            
        result = await self.session.execute(stmt)
        return list(result.unique().scalars())

    async def get_user(self, user_id: int) -> Optional[db_models.User]:
        """Get a user by ID."""
        stmt = (
            select(self.model)
            .options(
                joinedload(self.model.payment_methods),
                joinedload(self.model.trips),
                joinedload(self.model.transactions)
            )
            .where(self.model.id == user_id)
        )
        result = await self.session.execute(stmt)
        user = result.unique().scalar_one_or_none()
        
        if user is None:
            raise UserNotFoundException(f"User with ID {user_id} not found.")
        
        return user
    
    # async def create_user(self, user_data: dict[str, Any]) -> db_models.User:
    #     """Create a new user."""
    #     try:
    #         user = db_models.User(**user_data)
    #         self.session.add(user)
    #         await self.session.commit()
    #         stmt = (
    #             select(self.model)
    #             .options(
    #                 joinedload(self.model.payment_methods),
    #                 joinedload(self.model.trips),
    #                 joinedload(self.model.transactions)
    #             )
    #             .where(self.model.id == user.id)
    #         )
    #         result = await self.session.execute(stmt)
    #         return result.unique().scalar_one()
    #     except IntegrityError as e:
    #         await self.session.rollback()
    #         if 'users_email_key' in str(e):
    #             raise UserEmailExistsException(f"User with email {user_data['email']} already exists.")
    #         raise
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
            if 'users_email_key' in str(e):
                raise UserEmailExistsException(f"User with email {user_data['email']} already exists.")
            raise
    async def update_user(self, user_id: int, data: dict[str, Any]) -> Optional[db_models.User]:
        """Update a user by primary key."""
        query = (
            update(self.model)
            .where(self.model.id == user_id)
            .values(**data)
            .returning(self.model)
        )

        result = await self.session.execute(query)
        await self.session.commit()
        return result.unique().scalar_one_or_none()