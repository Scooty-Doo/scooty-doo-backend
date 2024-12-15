from collections.abc import Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# from database import database, models, repository
from db import database, repository
from models import db_models

def get_repository(model: type[db_models.Base]) -> Callable[[AsyncSession], repository.DatabaseRepository]:
    def func(session: AsyncSession = Depends(database.get_db_session)) -> repository.DatabaseRepository:
        return repository.DatabaseRepository(model, session)

    return func
