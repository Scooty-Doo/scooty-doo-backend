"""Repository module for database operations."""

import re
from typing import Any, Optional

from geoalchemy2.functions import ST_AsText
from geoalchemy2.shape import to_shape
from sqlalchemy import BinaryExpression, and_, select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from api.exceptions import ActiveTripExistsException
from api.db.repository_base import DatabaseRepository
from api.models import db_models


class TripRepository(DatabaseRepository[db_models.Trip]):
    """Repository for trip-specific operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with the Trip model."""
        super().__init__(db_models.Trip, session)

    def _get_trip_columns(self):
        """Get the columns to select for trip queries."""
        return [
            self.model.id,
            self.model.bike_id,
            self.model.user_id,
            self.model.start_time,
            self.model.end_time,
            ST_AsText(self.model.start_position).label("start_position"),
            ST_AsText(self.model.end_position).label("end_position"),
            ST_AsText(self.model.path_taken).label("path_taken"),
            self.model.start_fee,
            self.model.time_fee,
            self.model.end_fee,
            self.model.total_fee,
            self.model.created_at,
            self.model.updated_at,
        ]

    def _build_filters(self, filters: dict[str, Any]) -> list[BinaryExpression]:
        """Build SQLAlchemy filters from a dictionary of parameters.
        TODO This could be more general and moved to db"""
        expressions = []

        if filters.get("bike_id") is not None:
            expressions.append(self.model.bike_id == filters["bike_id"])

        if filters.get("user_id") is not None:
            expressions.append(self.model.user_id == filters["user_id"])

        return expressions

    async def get_trips(self, filters: Optional[dict[str, Any]] = None) -> list[db_models.Trip]:
        """Get trip with dynamic filters."""
        stmt = select(*self._get_trip_columns())

        if filters:
            expressions = self._build_filters(filters)
            if expressions:
                stmt = stmt.where(and_(*expressions))

        result = await self.session.execute(stmt)
        return list(result.mappings().all())

    async def get_trip(self, pk: int) -> Optional[db_models.Trip]:
        """Get a trip by ID."""
        stmt = select(*self._get_trip_columns()).where(self.model.id == pk)
        result = await self.session.execute(stmt)
        return result.mappings().first()

    async def add_trip(self, trip_data: dict[str, Any]) -> db_models.Trip:
        """Create a new trip"""
        bike_id = trip_data["bike_id"]
        user_id = trip_data["user_id"]
        subquery = select(db_models.Bike.last_position).where(db_models.Bike.id == bike_id).scalar_subquery()
        
        try:
            stmt = insert(db_models.Trip).values(
                user_id=user_id,
                bike_id=bike_id,
                start_position=subquery,
                start_fee=0,
            ).returning(*self._get_trip_columns())

            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.mappings().one()
        except IntegrityError as e:
            await self.session.rollback()
            if "idx_one_active_trip_per_user" in str(e):
                raise ActiveTripExistsException(
                    f"User {user_id} already has an active trip"
                )
            raise e


    # async def update_trip(self, pk: int, data: dict[str, Any]) -> Optional[db_models.Trip]:
    #     """Update a trip by primary key."""
    #     query = (
    #         update(self.model)
    #         .where(self.model.id == pk)
    #         .values(**data)
    #         .returning(*self._get_trip_columns())
    #     )

    #     result = await self.session.execute(query)
    #     await self.session.commit()
    #     return result.mappings().first()
