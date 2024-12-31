"""Repository module for database operations."""

from typing import Any, Optional

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.repository_base import DatabaseRepository
from api.exceptions import ZoneTypeNameExistsException, ZoneTypeNotFoundException
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
