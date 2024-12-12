from collections.abc import Callable

from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import database, models, repository

def get_repository(model: type[models.Base]) -> Callable[[AsyncSession], repository.DatabaseRepository]:
    def func(session: AsyncSession = Depends(database.get_db_session)) -> repository.DatabaseRepository:
        return repository.DatabaseRepository(model, session)

    return func


BikeRepository = Annotated[repository.DatabaseRepository[models.Bike], Depends(get_repository(models.Bike))]
