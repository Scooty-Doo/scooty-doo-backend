"""Repository module for database operations."""

from typing import Any, Optional

from geoalchemy2.functions import ST_AsText
from sqlalchemy import BinaryExpression, and_, asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_expression

from api.db.repository_base import DatabaseRepository
from api.models import db_models


class CityRepository(DatabaseRepository[db_models.City]):
    """Repository for  city-specific operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with the City model."""
        super().__init__(db_models.City, session)

    def _build_filters(self, **params: dict[str, Any]) -> list[BinaryExpression]:
        """Filter builder for  city queries."""
        filter_ = {
            "city_name_search": lambda v: self.model.city_name.ilike(f"%{v}%"),
            "city_id": lambda v: self.model.city_id == v,
        }

        return [
            filter_[key](value)
            for key, value in params.items()
            if key in filter_ and value is not None
        ]

    async def get_cities(self, **params: Optional[dict[str, Any]]) -> list[db_models.City]:
        """Get all  citys from the database."""
        stmt = select(self.model).options(
            with_expression(self.model.c_location, ST_AsText(self.model.c_location)),
        )
        if params:
            filters = self._build_filters(**params)
            stmt = stmt.where(and_(*filters))
        order_column = getattr(self.model, params.get("order_by", "id"))
        stmt = stmt.order_by(
            desc(order_column) if params.get("order_direction") == "desc" else asc(order_column)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
