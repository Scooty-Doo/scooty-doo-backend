"""Module for creating tables from sqlalchemy models"""

from sqlalchemy import text

from api.db.database import sessionmanager
from api.models.db_models import Base


async def load_tables():
    """Load the database tables."""

    async with sessionmanager.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with sessionmanager.connect() as conn:
        # Drop then create unique index so that a user can only have one active trip at a time
        await conn.execute(text("DROP INDEX IF EXISTS idx_one_active_trip_per_user;"))

        await conn.execute(
            text("""
                CREATE UNIQUE INDEX idx_one_active_trip_per_user 
                ON trips (user_id) 
                WHERE end_time IS NULL;
            """)
        )


async def main():
    """Main function to init the session manager and load the tables."""
    sessionmanager.init()
    await load_tables()
    await sessionmanager.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
