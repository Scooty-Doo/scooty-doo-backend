"""Repository module for database operations."""

from typing import Any

from sqlalchemy import BinaryExpression, and_, asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.repository_base import DatabaseRepository
from api.models import db_models


class TransactionRepository(DatabaseRepository[db_models.Transaction]):
    """Repository for transaction-specific operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with the Transaction model."""
        super().__init__(db_models.Transaction, session)

    def _build_filters(self, **params: dict[str, Any]) -> list[BinaryExpression]:
        """Filter builder for user queries."""
        filter_map = {
            "user_id": lambda v: self.model.user_id == v,
            "amount_gt": lambda v: self.model.amount > v,
            "amount_lt": lambda v: self.model.amount < v,
            "transaction_type": lambda v: self.model.transaction_type == v,
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

    async def get_transactions(self, **params: dict[str, Any]) -> list[db_models.Transaction]:
        """Get all transactions from the database."""
        stmt = select(self.model)

        filters = self._build_filters(**params)
        if filters:
            stmt = stmt.where(and_(*filters))  # Use filters, not params

        order_column = getattr(self.model, params.get("order_by", "created_at"))
        stmt = stmt.order_by(
            desc(order_column) if params.get("order_direction") == "desc" else asc(order_column)
        )

        stmt = stmt.offset(params.get("offset", 0)).limit(params.get("limit", 100))

        result = await self.session.execute(stmt)
        return list(result.scalars().unique())

    async def get_user_transactions(self, user_id: int) -> list[db_models.Transaction]:
        """Get all transactions for a user."""
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(stmt)
        transactions = result.unique().scalars()

        return transactions