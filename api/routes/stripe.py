"""Stripe routes"""

import stripe
from fastapi import APIRouter

from api.config import settings
from api.models.stripe_models import (
    PaymentUrlResponse,
    StripeModel,
    StripeResponse,
)

router = APIRouter(
    prefix="/v1/stripe",
    tags=["stripe"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def stripe_checkout(stripe_model: StripeModel) -> StripeResponse:
    """Creates a stripe checkout session"""
    stripe.api_key = settings.stripe_api_key
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {"price": "price_1Qcs7RKjM6yxgCD0ZwvITka8", "quantity": stripe_model.amount},
            ],
            mode="payment",
            success_url=stripe_model.frontend_url
            + "?success=true&session_id={CHECKOUT_SESSION_ID}",
            cancel_url=stripe_model.frontend_url + "?canceled=true",
        )
    except Exception as e:
        return str(e)

    return StripeResponse(data=PaymentUrlResponse(url=checkout_session.url))
