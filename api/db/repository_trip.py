"""Repository module for database operations."""

import decimal
import re
from datetime import datetime
from typing import Any, Optional

from geoalchemy2.functions import ST_AsText
from geoalchemy2.shape import to_shape
from sqlalchemy import BinaryExpression, and_, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.repository_base import DatabaseRepository
from api.exceptions import (
    ActiveTripExistsException,
    TripAlreadyEndedException,
    TripNotFoundException,
    UnauthorizedTripAccessException,
)
from api.models import db_models
from api.models.trip_models import TripCreate, TripEndRepoParams


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

    async def add_trip(self, trip_data: TripCreate) -> db_models.Trip:
        """Create a new trip using validated data from bike service."""
        try:
            stmt = (
                insert(db_models.Trip)
                .values(**trip_data.model_dump())
                .returning(*self._get_trip_columns())
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.mappings().one()
        except IntegrityError as e:
            await self.session.rollback()
            if "idx_one_active_trip_per_user" in str(e):
                raise ActiveTripExistsException(
                    f"User {trip_data.user_id} already has an active trip"
                )
            raise e

    def _calculate_fees(
        self, start_time: datetime, end_time: datetime
    ) -> dict[str, decimal.Decimal]:
        """Calculate trip fees."""
        print(f"Calculating fees from {start_time} to {end_time}")
        time_fee = decimal.Decimal("0.5")
        print("TIME_FEE", time_fee)
        minutes = decimal.Decimal(str((end_time - start_time).total_seconds() / 60))
        print("MINUTES", minutes)
        fees = {
            "start_fee": decimal.Decimal("10"),
            "time_fee": time_fee * minutes,
            "end_fee": decimal.Decimal("0"),
        }
        print("FEES:", fees)
        fees["total_fee"] = sum(fees.values())
        print(f"Calculated fees: {fees}")
        return fees

    async def end_trip(self, params: TripEndRepoParams, is_available: bool = True) -> tuple[Optional[db_models.Trip], Optional[db_models.User], Optional[db_models.Transaction]]:
        async with self.session.begin():
            stmt = select(*self._get_trip_columns()).where(self.model.id == params.trip_id)
            result = await self.session.execute(stmt)
            trip = result.mappings().first()

            # chekc if trip exists, is owned by the user, and is not already ended
            if not trip:
                raise TripNotFoundException(f"Trip {params.trip_id} not found")
            if trip.user_id != params.user_id:
                raise UnauthorizedTripAccessException(
                    f"User {params.user_id} does not own trip {params.trip_id}"
                )
            if trip.end_time:
                raise TripAlreadyEndedException(f"Trip {params.trip_id} is already ended")

            fees = self._calculate_fees(trip.start_time, params.end_time)
            update_data = {
                "end_time": params.end_time,
                "end_position": params.end_position,
                "path_taken": params.path_taken,
                **fees,
            }

            updated_trip_result = await self.session.execute(
                update(self.model)
                .where(self.model.id == params.trip_id)
                .values(**update_data)
                .returning(*self._get_trip_columns())
            )
            updated_trip = updated_trip_result.mappings().first()

            updated_user_balance_result = await self.session.execute(
                update(db_models.User)
                .where(db_models.User.id == params.user_id)
                .values(balance=db_models.User.balance - fees["total_fee"])
                .returning(db_models.User)
            )
            updated_user_balance = updated_user_balance_result.mappings().first()

            created_transaction_result = await self.session.execute(
                insert(db_models.Transaction).values(
                    trip_id=params.trip_id,
                    user_id=params.user_id,
                    amount=fees["total_fee"],
                    transaction_type="trip",
                ).returning(db_models.Transaction)
            )
            created_transaction = created_transaction_result.mappings().first()

            # Check if the bike is_available has changed and update if it has
            if is_available:
                await self.session.execute(
                    update(db_models.Bike)
                    .where(db_models.Bike.id == trip.bike_id)
                    .values(is_available=True)
                )

            await self.session.commit()
            return updated_trip