"""Module for creating tables from sqlalchemy models"""

from api.db.database import sessionmanager
from api.models.db_models import Base


async def load_tables():
    """Load the database tables."""
    async with sessionmanager.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def main():
    """Main function to init the session manager and load the tables."""
    sessionmanager.init()

    await load_tables()

    await sessionmanager.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
