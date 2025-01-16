"""Repository module for database operations."""

import decimal
from datetime import datetime
from typing import Any, Optional

from geoalchemy2.functions import ST_AsText
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

    def _build_filters(self, **params: dict[str, Any]) -> list[BinaryExpression]:
        """Filter builder for trip queries."""
        filter_map = {
            "bike_id": lambda v: self.model.bike_id == v,
            "user_id": lambda v: self.model.user_id == v,
            "total_fee_gt": lambda v: self.model.total_fee > v,
            "total_fee_lt": lambda v: self.model.total_fee < v,
            "start_time": lambda v: self.model.start_time == v,
            "end_time": lambda v: self.model.end_time == v,
            "created_at_gt": lambda v: self.model.created_at > v,
            "created_at_lt": lambda v: self.model.created_at < v,
            "updated_at_gt": lambda v: self.model.updated_at > v,
            "updated_at_lt": lambda v: self.model.updated_at < v,
            "is_ongoing": lambda v: self.model.end_time.is_(None)
            if v
            else self.model.end_time.isnot(None),
        }

        return [
            filter_map[key](value)
            for key, value in params.items()
            if key in filter_map and value is not None
        ]

    async def get_trips(self, **params) -> list[db_models.Trip]:
        """Get trip with dynamic filters."""
        stmt = select(*self._get_trip_columns())

        filters = self._build_filters(**params)
        if filters:
            stmt = stmt.where(and_(*filters))

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

            # set bike to unavailable
            await self.session.execute(
                update(db_models.Bike)
                .where(db_models.Bike.id == trip_data.bike_id)
                .values(is_available=False)
            )

            await self.session.commit()
            return result.mappings().one()
        except IntegrityError as e:
            await self.session.rollback()
            if "idx_one_active_trip_per_user" in str(e):
                raise ActiveTripExistsException(
                    f"User {trip_data.user_id} already has an active trip"
                ) from e
            raise e

    def _calculate_fees(
        self, start_time: datetime, end_time: datetime
    ) -> dict[str, decimal.Decimal]:
        """Calculate trip fees."""
        time_fee = decimal.Decimal("0.5")
        minutes = decimal.Decimal(str((end_time - start_time).total_seconds() / 60))
        fees = {
            "start_fee": decimal.Decimal("10"),
            "time_fee": time_fee * minutes,
            "end_fee": decimal.Decimal("0"),
        }
        fees["total_fee"] = sum(fees.values())
        return fees

    async def end_trip(
        self, params: TripEndRepoParams, is_available: bool = True
    ) -> tuple[Optional[db_models.Trip], Optional[db_models.User], Optional[db_models.Transaction]]:
        """End a trip and update user balance."""
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

            # Commented out code to use if we want to return more than just the trip data
            # updated_user_balance_result =
            await self.session.execute(
                update(db_models.User)
                .where(db_models.User.id == params.user_id)
                .values(balance=db_models.User.balance - fees["total_fee"])
                # .returning(db_models.User)
            )
            # updated_user_balance = updated_user_balance_result.mappings().first()

            # Commented out code to use if we want to return more than just the trip data
            # created_transaction_result =
            await self.session.execute(
                insert(db_models.Transaction).values(
                    trip_id=params.trip_id,
                    user_id=params.user_id,
                    amount=fees["total_fee"],
                    transaction_type="trip",
                )
                # .returning(db_models.Transaction)
            )
            # created_transaction = created_transaction_result.mappings().first()

            # Check if the bike is_available has changed and update if it has
            if is_available:
                await self.session.execute(
                    update(db_models.Bike)
                    .where(db_models.Bike.id == trip.bike_id)
                    .values(is_available=True)
                )

            await self.session.commit()
            return updated_trip
