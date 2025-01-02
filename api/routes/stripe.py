"""Stripe routes"""

import os
import stripe
from fastapi import APIRouter, Request
from dotenv import load_dotenv
from api.models.stripe_models import StripeModel, StripeResponse, PaymentUrlResponse

router = APIRouter(
    prefix="/v1/stripe",
    tags=["stripe"],
    responses={404: {"description": "Not found"}},
)

load_dotenv()

@router.post("/")
async def stripe_checkout(request: Request, stripe_model: StripeModel) -> StripeResponse:
    """Creates a stripe checkout session"""
    stripe.api_key = os.getenv("STRIPE_API_KEY")
    print(stripe_model.frontend_url)
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price": "price_1Qcs7RKjM6yxgCD0ZwvITka8",
                    "quantity": stripe_model.amount
                },
            ],
            mode="payment",
            success_url=stripe_model.frontend_url + "?success=true",
            cancel_url=stripe_model.frontend_url + "?canceled=true",
        )
    except Exception as e:
        return str(e)

    return StripeResponse(data=PaymentUrlResponse(url=checkout_session.url))
