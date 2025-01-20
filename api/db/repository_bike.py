"""Repository module for database operations."""

from typing import Any, Optional

from geoalchemy2.functions import ST_AsText
from sqlalchemy import BinaryExpression, and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_expression

from api.db.repository_base import DatabaseRepository
from api.exceptions import BikeNotFoundException
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
            self.model.deleted_at,
            ST_AsText(self.model.last_position).label("last_position"),
        ]

    def _build_filters(self, **params: dict[str, Any]) -> list[BinaryExpression]:
        """Filter builder for user queries."""
        filter_map = {
            "is_available": lambda v: self.model.is_available == v,
            "city_id": lambda v: self.model.city_id == v,
            "min_battery": lambda v: self.model.battery_lvl > v,
            "max_battery": lambda v: self.model.battery_lvl < v,
            "created_at_gt": lambda v: self.model.created_at > v,
            "created_at_lt": lambda v: self.model.created_at < v,
            "updated_at_gt": lambda v: self.model.updated_at > v,
            "updated_at_lt": lambda v: self.model.updated_at < v,
        }

        filters = [
            filter_map[key](value)
            for key, value in params.items()
            if key in filter_map and value is not None
        ]

        include_deleted = params.get("include_deleted", False)
        if not include_deleted:
            filters.append(self.model.deleted_at.is_(None))

        return filters

    async def get_bikes(self, **params) -> list[db_models.Bike]:
        """Get bikes with dynamic filters."""
        stmt = select(*self._get_bike_columns())

        filters = self._build_filters(**params)
        if filters:
            stmt = stmt.where(and_(*filters))
        order_column = getattr(self.model, params.get("order_by", "created_at"))
        stmt = stmt.order_by(order_column)

        stmt = stmt.offset(params.get("offset", 0)).limit(params.get("limit", 100))

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
        bike_exists = await self.session.execute(
            select(self.model).where(self.model.id == pk).where(self.model.deleted_at.is_(None))
        )
        bike_exists = bike_exists.scalar_one_or_none()
        if bike_exists is None:
            raise BikeNotFoundException(f"Bike with ID {pk} not found")

        query = (
            update(self.model)
            # where bike id matches and bike is not deleted
            .where(self.model.id == pk)
            .values(**data)
            .returning(*self._get_bike_columns())
        )

        result = await self.session.execute(query)
        await self.session.commit()
        return result.mappings().first()

    async def get_bike(self, pk: int) -> Optional[db_models.Bike]:
        """Get a bike by ID."""
        stmt = (
            select(self.model)
            .options(with_expression(self.model.last_position, ST_AsText(self.model.last_position)))  # noqa: F821
            .where(self.model.id == pk)
        )

        result = await self.session.execute(stmt)
        bike = result.unique().scalar_one_or_none()

        if bike is None:
            raise BikeNotFoundException(f"Bike with ID {pk} not found")

        return bike

    async def get_bikes_in_zone(
        self, zone_type_id: int, city_id: int
    ) -> list[tuple[db_models.Bike, int]]:
        """Get bikes in a given zone and city."""
        stmt = (
            select(self.model, db_models.MapZone.id.label("map_zone_id"))
            .join(
                db_models.MapZone,
                func.ST_Contains(db_models.MapZone.boundary, self.model.last_position),  # noqa: F821
            )
            .options(with_expression(self.model.last_position, ST_AsText(self.model.last_position)))  # noqa: F821
            .where(db_models.MapZone.zone_type_id == zone_type_id)
            .where(self.model.city_id == city_id)
        )

        result = await self.session.execute(stmt)
        return result.all()

    async def delete_bike(self, bike_id: int) -> Optional[db_models.Bike]:
        """Soft delete a bike."""
        stmt = (
            update(self.model)
            .where(self.model.id == bike_id)
            .where(self.model.deleted_at.is_(None))
            .values(
                deleted_at=func.now(),
                is_available=False,
                last_position=None,
                battery_lvl=0,
            )
            .returning(*self._get_bike_columns())
        )

        result = await self.session.execute(stmt)
        bike = result.mappings().one_or_none()

        if not bike:
            raise BikeNotFoundException(f"Bike with ID {bike_id} not found")

        await self.session.commit()
        return bike
