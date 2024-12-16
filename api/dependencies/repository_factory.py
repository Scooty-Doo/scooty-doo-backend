from collections.abc import Callable
from typing import Type, TypeVar

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.db import database, repository
from api.models import db_models

Model = TypeVar("Model", bound=db_models.Base)
Repo = TypeVar("Repo", bound=repository.DatabaseRepository)

def get_repository(
    model: type[Model],
    repository_class: Type[Repo] = repository.DatabaseRepository
) -> Callable[[AsyncSession], Repo]:
    """Get a repository instance for a model.
    
    Args:
        model: The SQLAlchemy model class
        repository_class: Optional custom repository class. Defaults to DatabaseRepository.
    
    Returns:
        A function that creates a repository instance when called with a database session.
    """
    def func(session: AsyncSession = Depends(database.get_db_session)) -> Repo:
        if repository_class == repository.DatabaseRepository:
            return repository_class(model, session)
        return repository_class(session)

    return func
