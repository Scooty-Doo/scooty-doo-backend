import uuid
from typing import Generic, TypeVar, Any
from sqlalchemy import BinaryExpression, select, delete, update, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import models

Model = TypeVar("Model", bound=models.Base)

class DatabaseRepository(Generic[Model]):
    """Repository for performing database queries."""

    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def create(self, data: dict[str, Any]) -> Model:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get(self, pk: int | uuid.UUID) -> Model | None:
        return await self.session.get(self.model, pk)

    async def filter(
        self,
        *expressions: BinaryExpression,
    ) -> list[Model]:
        query = select(self.model)
        if expressions:
            query = query.where(*expressions)
        return list(await self.session.scalars(query))

    async def update(self, pk: int | uuid.UUID, data: dict[str, Any]) -> Model | None:
        query = (
            update(self.model)
            .where(self.model.id == pk)
            .values(**data)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, pk: int | uuid.UUID) -> bool:
        query = delete(self.model).where(self.model.id == pk)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0
    
class BikeRepository(DatabaseRepository[models.Bike]):
    async def get_available(self) -> list[models.Bike]:
        query = (
            select(self.model)
            .join(models.Bike2BikeStatus)
            .join(models.BikeStatus)
            .where(models.BikeStatus.status_code == "AVAILABLE")
            .options(joinedload(self.model.statuses))
        )
        result = await self.session.scalars(query)
        return list(result)