"""Database connection and session management.

This module provides the core database functionality for the application:
1. Database engine creation and configuration
2. Session management with context managers
3. FastAPI dependency for database sessions
"""

import contextlib
from typing import AsyncGenerator, AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.declarative import declarative_base

# import os
# import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import settings from config.py
from config import settings

Base = declarative_base()

class DatabaseSessionManager:
    """Manages database sessions and connections.
    
    This class handles the lifecycle of database connections and sessions:
    - Creates and configures the SQLAlchemy engine
    - Provides context managers for connections and sessions
    - Handles cleanup of resources
    
    Usage:
        manager = DatabaseSessionManager()
        manager.init()  # Initialize on startup
        
        async with manager.session() as session:
            # Use session for database operations
    """

    def __init__(self):
        """Initialize manager with no engine or session maker."""
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker | None = None

    def init(self, url: str = settings.database_url):
        """Initialize database engine and session maker.
        
        Args:
            url: Database connection URL. Defaults to URL from settings.
        """
        self._engine = create_async_engine(
            url,
            pool_pre_ping=True,  # Verify connection before using from pool
            pool_size=10,        # Number of connections to maintain
            max_overflow=10,  # max extra connections to create
            echo=settings.debug,  # SQL logging
        )
        self._sessionmaker = async_sessionmaker(
            autocommit=False,
            bind=self._engine,
            expire_on_commit=False,  # Don't expire objects after commit
        )

    async def close(self):
        """Close database connections and cleanup resources."""
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        """Get a database connection.
        
        Provides transaction management and automatic rollback on errors.
        
        Yields:
            AsyncConnection: Database connection
        
        Raises:
            Exception: If manager not initialized
        """
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Get a database session.
        
        Provides transaction management and automatic cleanup.
        
        Yields:
            AsyncSession: Database session
            
        Raises:
            Exception: If manager not initialized
        """
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    # Used for testing
    async def create_all(self, connection: AsyncConnection):
        await connection.run_sync(Base.metadata.create_all)

    async def drop_all(self, connection: AsyncConnection):
        await connection.run_sync(Base.metadata.drop_all)

# Global session manager instance
sessionmanager = DatabaseSessionManager()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions.
    
    Usage:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_db_session)):
            ...
    
    Yields:
        AsyncSession: Database session that's automatically cleaned up
    """
    async with sessionmanager.session() as session:
        yield session
