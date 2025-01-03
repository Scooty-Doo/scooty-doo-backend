"""MOdule with models for OAuth2"""

from pydantic import BaseModel, Field
from typing import Annotated


class StripeModel(BaseModel):
    """Model for incoming data to the stripe checkout screen."""
    frontend_url: str = Field(example="http://www.scootydoo.com/#homeclient")
    amount: Annotated[int, Field(ge=3)]

class PaymentUrlResponse(BaseModel):
    """Response model for a payment URL."""

    url: str = Field(..., description="Checkout URL for payment", example="https://checkout.stripe.com/c/pay/awdaoOiawhd1cXdwYHgl")

class StripeResponse(BaseModel):
    """JSON:API resource for the payment URL."""

    data: PaymentUrlResponse

class StripeSuccess(BaseModel):
    """Model for incoming data on stripe success"""
    session_id: str
