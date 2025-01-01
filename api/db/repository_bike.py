"""Repository module for database operations."""

from typing import Any, Optional

from geoalchemy2.functions import ST_AsText
from sqlalchemy import BinaryExpression, and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.repository_base import DatabaseRepository
from api.models import db_models


class BikeRepository(DatabaseRepository[db_models.Bike]):
    """Repository for bike-specific operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with the Bike model."""
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
            ST_AsText(self.model.last_position).label("last_position"),
        ]

    def _build_filters(self, filters: dict[str, Any]) -> list[BinaryExpression]:
        """Build SQLAlchemy filters from a dictionary of parameters."""
        expressions = []

        if filters.get("city_id") is not None:
            expressions.append(self.model.city_id == filters["city_id"])

        if filters.get("is_available") is not None:
            expressions.append(self.model.is_available == filters["is_available"])

        if filters.get("min_battery") is not None:
            expressions.append(self.model.battery_lvl >= filters["min_battery"])

        if filters.get("max_battery") is not None:
            expressions.append(self.model.battery_lvl <= filters["max_battery"])

        return expressions

    async def get_bikes(self, filters: Optional[dict[str, Any]] = None) -> list[db_models.Bike]:
        """Get bikes with dynamic filters."""
        stmt = select(*self._get_bike_columns())

        if filters:
            expressions = self._build_filters(filters)
            if expressions:
                stmt = stmt.where(and_(*expressions))

        result = await self.session.execute(stmt)
        return list(result.mappings().all())

    async def add_bike(self, bike_data: dict[str, Any]) -> db_models.Bike:
        """Add a new bike to the database.
        TODO: Use WKT transformation like in update_bike"""
        db_bike = db_models.Bike(**bike_data)
        self.session.add(db_bike)
        await self.session.commit()
        await self.session.refresh(db_bike)

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

    async def get_bike(self, pk: int) -> Optional[db_models.Bike]:
        """Get a bike by ID."""
        stmt = select(*self._get_bike_columns()).where(self.model.id == pk)
        result = await self.session.execute(stmt)
        return result.mappings().first()
