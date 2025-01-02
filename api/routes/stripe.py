"""Stripe routes"""

import os
import stripe
from fastapi import APIRouter, Request
from dotenv import load_dotenv

from starlette.responses import RedirectResponse
from api.models.stripe_models import StripeModel
router = APIRouter(
    prefix="/v1/stripe",
    tags=["stripe"],
    responses={404: {"description": "Not found"}},
)

load_dotenv()

@router.post("/stripe-checkout")
async def stripe_checkout(request: Request, stripe_model: StripeModel):
    """Creates a stripe checkout session"""
    stripe.api_key = os.getenv("STRIPE_API_KEY")
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price": "price_1Qcs7RKjM6yxgCD0ZwvITka8",
                    "quantity": stripe_model.amount
                },
                
            ],
            mode="payment",
            success_url=str(request.base_url) + "?success=true",
            cancel_url=str(request.base_url) + "?canceled=true",
        )
    except Exception as e:
        return str(e)

    return RedirectResponse(url=checkout_session.url, status_code=303)
