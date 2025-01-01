"""Repository module for database operations."""

from typing import Any, Optional

from geoalchemy2.functions import ST_AsText
from sqlalchemy import select, update, and_, desc, asc, BinaryExpression
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload, with_expression

from api.db.repository_base import DatabaseRepository
from api.exceptions import ZoneTypeNameExistsException, ZoneTypeNotFoundException, MapZoneNotFoundException
from api.models import db_models


class ZoneTypeRepository(DatabaseRepository[db_models.ZoneType]):
    """Repository for zone type-specific operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with the ZoneType model."""
        super().__init__(db_models.ZoneType, session)

    async def get_zone_types(self) -> list[db_models.ZoneType]:
        """Get all zone types."""
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def create_zone_type(self, zone_type_data: dict[str, Any]) -> db_models.ZoneType:
        """Create a new zone type."""
        try:
            zone_type = db_models.ZoneType(**zone_type_data)
            self.session.add(zone_type)
            await self.session.commit()

            await self.session.refresh(zone_type)
            return zone_type
        except IntegrityError as e:
            await self.session.rollback()
            if "zone_types_name_key" in str(e):
                raise ZoneTypeNameExistsException(
                    f"Zone type with name {zone_type_data['name']} already exists."
                ) from e
            raise

    async def update_zone_type(
        self, zone_type_id: int, data: dict[str, Any]
    ) -> Optional[db_models.ZoneType]:
        """Update a zone type by primary key."""
        try:
            stmt = (
                update(self.model)
                .where(self.model.id == zone_type_id)
                .values(**data)
                .returning(*self.model.__table__.columns)
            )

            result = await self.session.execute(stmt)
            await self.session.commit()

            updated_zone = result.mappings().one_or_none()
            if not updated_zone:
                raise ZoneTypeNotFoundException(f"Zone type with ID {zone_type_id} not found.")

            return updated_zone

        except IntegrityError as e:
            await self.session.rollback()
            if "zone_types_name_key" in str(e):
                raise ZoneTypeNameExistsException(f"Name {data.get('name')} already exists.") from e
            raise

class MapZoneRepository(DatabaseRepository[db_models.MapZone]):
    """Repository for map zone-specific operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with the MapZone model."""
        super().__init__(db_models.MapZone, session)
    
    def _get_map_zone_columns(self) -> list:
        """Get columns for map zone queries."""
        return [
            self.model.id,
            self.model.zone_name,
            self.model.zone_type_id,
            self.model.city_id,
            ST_AsText(self.model.boundary).label("boundary"),
            self.model.created_at,
            self.model.updated_at,
        ]
    def _build_filters(self, **params: dict[str, Any]) -> list[BinaryExpression]:
        """Filter builder for map zone queries."""
        filter_map = {
            "zone_name_search": lambda v: self.model.zone_name.ilike(f"%{v}%"),
            "city_id": lambda v: self.model.city_id == v,
            "zone_type_id": lambda v: self.model.zone_type_id == v,
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

    async def get_map_zones(self, **params: dict[str, Any]) -> list[db_models.MapZone]:
        """Get all map zones from the database."""
        stmt = select(*self._get_map_zone_columns())

        filters = self._build_filters(**params)
        if filters:
            stmt = stmt.where(and_(*filters))

        order_column = getattr(self.model, params.get("order_by", "created_at"))
        stmt = stmt.order_by(
            desc(order_column) if params.get("order_direction") == "desc" else asc(order_column)
        )

        stmt = stmt.offset(params.get("offset", 0)).limit(params.get("limit", 100))

        result = await self.session.execute(stmt)
        return list(result.mappings().all())
    
    async def get_map_zone(self, pk: int) -> Optional[db_models.MapZone]:
        """Get a map zone by ID with relationships."""
        stmt = (
            select(self.model)
            .options(
                selectinload(self.model.city),
                selectinload(self.model.zone_type),
                with_expression(self.model.boundary, ST_AsText(self.model.boundary))
            )
            .where(self.model.id == pk)
        )
        
        result = await self.session.execute(stmt)
        zone = result.unique().scalar_one_or_none()
        
        if zone is None:
            raise MapZoneNotFoundException(f"Map zone with ID {pk} not found.")
        
        return zone