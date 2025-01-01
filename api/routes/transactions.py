"""Module for the /users routes"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from api.db.repository_transaction import TransactionRepository as TransactionRepoClass
from api.dependencies.repository_factory import get_repository
from api.models import db_models
from api.models.models import (
    JsonApiLinks,
    JsonApiResponse,
)
from api.models.transaction_models import TransactionGetRequestParams, TransactionResourceMinimal

router = APIRouter(
    prefix="/v1/transactions",
    tags=["transactions"],
    responses={404: {"description": "Not found"}},
)

TransactionRepository = Annotated[
    TransactionRepoClass,
    Depends(get_repository(db_models.Transaction, repository_class=TransactionRepoClass)),
]


@router.get("/", response_model=JsonApiResponse[TransactionResourceMinimal])
async def get_transactions(
    transaction_repository: TransactionRepository,
    request: Request,
    query_params: Annotated[TransactionGetRequestParams, Query()],
) -> JsonApiResponse[TransactionResourceMinimal]:
    """Get transactions from the db. Defaults to showing first 100 transactions"""
    transactions = await transaction_repository.get_transactions(
        **query_params.model_dump(exclude_none=True)
    )
    base_url = str(request.base_url).rstrip("/")
    collection_url = f"{base_url}/v1/transactions"

    return JsonApiResponse(
        data=[
            TransactionResourceMinimal.from_db_model(
                transaction, f"{collection_url}/{transaction.id}"
            )
            for transaction in transactions
        ],
        links=JsonApiLinks(self=collection_url),
    )
