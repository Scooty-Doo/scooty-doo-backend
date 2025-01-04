"""Stripe routes"""

import os

import stripe
from dotenv import load_dotenv
from fastapi import APIRouter

from api.models.stripe_models import (
    NewBalance,
    PaymentUrlResponse,
    StripeModel,
    StripeResponse,
    StripeSuccess,
    StripeSuccessResponse,
)

router = APIRouter(
    prefix="/v1/stripe",
    tags=["stripe"],
    responses={404: {"description": "Not found"}},
)

load_dotenv()


@router.post("/")
async def stripe_checkout(stripe_model: StripeModel) -> StripeResponse:
    """Creates a stripe checkout session"""
    stripe.api_key = os.getenv("STRIPE_API_KEY")
    print(stripe_model.frontend_url)
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


@router.post("/success", response_model=StripeSuccessResponse)
async def stripe_success(success_data: StripeSuccess) -> StripeSuccessResponse:
    """Creates a transaction in the database on succesful stripe payment."""
    session = stripe.checkout.Session.retrieve(success_data.session_id)
    amount_in_kr = session.amount_subtotal / 100  # Så här mycket fick vi in!
    # Skapa transaction
    # Uppdatera user
    # Hämta uppdaterad user

    return StripeSuccessResponse(data=NewBalance(balance=amount_in_kr))
