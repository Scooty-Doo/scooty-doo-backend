"""Stripe routes"""

import os
import stripe
from fastapi import APIRouter, Request
from dotenv import load_dotenv
from api.models.stripe_models import StripeModel, StripeResponse, PaymentUrlResponse
from fastapi.encoders import jsonable_encoder

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

    return StripeResponse(data=PaymentUrlResponse(url=checkout_session.url))
    #return jsonable_encoder(checkout_session.url)
    #return JsonApiResponse(data={"url": checkout_session.url}, links=JsonApiLinks(self_link=checkout_session.url))
