"""Repository module for database operations."""

from typing import Any, Generic, TypeVar

from sqlalchemy import BinaryExpression, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import db_models

Model = TypeVar("Model", bound=db_models.Base)


class DatabaseRepository(Generic[Model]):
    """Base repository for performing database queries."""

    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def add(self, instance: Model) -> Model:
        """Add a new instance to the database."""
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get(self, pk: int) -> Model | None:
        """Get an instance by primary key."""
        return await self.session.get(self.model, pk)

    async def get_all(self) -> list[Model]:
        """Get all instances."""
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def filter(
        self,
        *expressions: BinaryExpression,
    ) -> list[Model]:
        """Filter instances by expressions."""
        stmt = select(self.model)
        if expressions:
            stmt = stmt.where(*expressions)
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def update(self, pk: int, data: dict[str, Any]) -> Model | None:
        """Update an instance by primary key."""
        query = update(self.model).where(self.model.id == pk).values(**data).returning(self.model)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, pk: int) -> bool:
        """Delete an instance by primary key."""
        query = delete(self.model).where(self.model.id == pk)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

    async def count(self, *expressions: BinaryExpression) -> int:
        """Count instances matching expressions."""
        # pylint: disable=not-callable
        query = select(func.count()).select_from(self.model)
        if expressions:
            query = query.where(*expressions)
        result = await self.session.scalar(query)
        return result or 0

    async def get_first(self, *expressions: BinaryExpression) -> Model | None:
        """Get the first instance matching expressions."""
        query = select(self.model)
        if expressions:
            query = query.where(*expressions)
        result = await self.session.scalars(query)
        return result.first()

    async def get_last(self, *expressions: BinaryExpression) -> Model | None:
        """Get the last instance matching expressions."""
        query = select(self.model)
        if expressions:
            query = query.where(*expressions)
        result = await self.session.scalars(query)
        return result.last()

    async def exists(self, *expressions: BinaryExpression) -> bool:
        """Check if an instance matching expressions exists."""
        query = select(self.model)
        if expressions:
            query = query.where(*expressions)
        result = await self.session.scalars(query)
        return result.first() is not None
