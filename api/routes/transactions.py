"""Module for the /users routes"""

from decimal import Decimal
from typing import Annotated

import stripe
from fastapi import APIRouter, Depends, Query, Request, Security

from api.db.repository_transaction import TransactionRepository as TransactionRepoClass
from api.dependencies.repository_factory import get_repository
from api.models import db_models
from api.models.models import (
    JsonApiLinks,
    JsonApiResponse,
)
from api.models.transaction_models import (
    TransactionGetRequestParams,
    TransactionResourceMinimal,
    TransactionResourceWithBalance,
)
from api.services.oauth import security_check

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
    _: Annotated[int, Security(security_check, scopes=["admin"])],
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
        links=JsonApiLinks(self_link=collection_url),
    )


@router.post("/", response_model=JsonApiResponse[TransactionResourceWithBalance])
async def add_transaction(
    user_id: Annotated[int, Security(security_check, scopes=["user"])],
    request: Request,
    session_data: dict,
    transaction_repository: TransactionRepository,
) -> JsonApiResponse[TransactionResourceWithBalance]:
    """Add a transaction to the db"""
    stripe_session = stripe.checkout.Session.retrieve(session_data["session_id"])
    amount_in_kr = stripe_session.amount_subtotal / 100
    payment_intent = stripe_session.payment_intent

    transaction_data = {
        "user_id": user_id,
        "amount": amount_in_kr,
        "payment_intent_id": payment_intent,
        "transaction_type": "deposit",
        "transaction_description": "Stripe payment",
    }
    transaction, user_balance = await transaction_repository.add_transaction(transaction_data)
    user_balance_decimal = Decimal(str(user_balance))
    base_url = str(request.base_url).rstrip("/")
    collection_url = f"{base_url}/v1/transactions"
    transaction_url = f"{collection_url}/{transaction.id}"

    return JsonApiResponse(
        data=TransactionResourceWithBalance.from_db_model(
            transaction=transaction, request_url=transaction_url, user_balance=user_balance_decimal
        ),
        links=JsonApiLinks(self_link=collection_url),
    )
