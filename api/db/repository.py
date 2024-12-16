"""Repository module for database operations."""
from typing import Generic, TypeVar, Any, List, Sequence, Dict, Optional
from sqlalchemy import BinaryExpression, select, delete, update, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from geoalchemy2.functions import ST_AsText
from shapely.wkt import dumps
from geoalchemy2.shape import to_shape
from api.models import db_models
import re

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
        query = (
            update(self.model)
            .where(self.model.id == pk)
            .values(**data)
            .returning(self.model)
        )
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


class BikeRepository(DatabaseRepository[db_models.Bike]):
    """Repository for bike-specific operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(db_models.Bike, session)

    def _get_bike_columns(self):
        """Get the columns to select for bike queries."""
        return [
            self.model.id,
            self.model.battery_lvl,
            self.model.city_id,
            self.model.is_available,
            self.model.meta_data,
            self.model.created_at,
            self.model.updated_at,
            ST_AsText(self.model.last_position).label('last_position')
        ]

    def _ewkb_to_wkt(self, ewkb) -> str:
        """Remove the first space from a WKT string."""
        wkt = to_shape(ewkb).wkt
        return re.sub(r'POINT \(', 'POINT(', wkt)

    def _build_filters(self, filters: dict[str, Any]) -> list[BinaryExpression]:
        """Build SQLAlchemy filters from a dictionary of parameters."""
        expressions = []
        
        if filters.get('city_id') is not None:
            expressions.append(self.model.city_id == filters['city_id'])
        
        if filters.get('is_available') is not None:
            expressions.append(self.model.is_available == filters['is_available'])
        
        if filters.get('min_battery') is not None:
            expressions.append(self.model.battery_lvl >= filters['min_battery'])
        
        if filters.get('max_battery') is not None:
            expressions.append(self.model.battery_lvl <= filters['max_battery'])
        
        return expressions

    async def get_bikes(self, filters: Optional[Dict[str, Any]] = None) -> list[db_models.Bike]:
        """Get bikes with dynamic filters."""
        stmt = select(*self._get_bike_columns())
        
        if filters:
            expressions = self._build_filters(filters)
            if expressions:
                stmt = stmt.where(and_(*expressions))
        
        result = await self.session.execute(stmt)
        return list(result.mappings().all())

    async def add_bike(self, bike_data: Dict[str, Any]) -> db_models.Bike:
        """Add a new bike to the database.
        TODO: Use WKT transformation like in update_bike"""
        db_bike = db_models.Bike(**bike_data)
        self.session.add(db_bike)
        await self.session.commit()
        await self.session.refresh(db_bike)

        #convert to wkt and remove the space between POINT and the coordinates
        db_bike.last_position = self._ewkb_to_wkt(db_bike.last_position)
        return db_bike

    async def update_bike(self, pk: int, data: dict[str, Any]) -> Optional[db_models.Bike]:
        """Update a bike by primary key."""
        query = (
            update(self.model)
            .where(self.model.id == pk)
            .values(**data)
            .returning(*self._get_bike_columns())
        )

        result = await self.session.execute(query)
        await self.session.commit()
        return result.mappings().first()

    async def get(self, id_: int) -> Optional[db_models.Bike]:
        """Get a bike by ID."""
        stmt = select(*self._get_bike_columns()).where(self.model.id == id_)
        result = await self.session.execute(stmt)
        return result.mappings().first()

