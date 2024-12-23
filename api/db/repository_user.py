"""Repository module for database operations."""

import re
from typing import Any, Optional

from geoalchemy2.functions import ST_AsText
from geoalchemy2.shape import to_shape
from sqlalchemy import BinaryExpression, and_, select, update, desc, asc
from sqlalchemy.orm import joinedload
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