
# Import your models from models.py
from models import Base
# Import the session manager
from database import sessionmanager


async def load_tables():
    async with sessionmanager.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def main():
    # Initialize the session manager
    sessionmanager.init()
    
    # Load the tables
    await load_tables()
    
    # Optionally, close the session manager
    await sessionmanager.close()

# Run the main function
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())