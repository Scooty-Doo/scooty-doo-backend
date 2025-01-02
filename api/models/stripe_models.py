"""MOdule with models for OAuth2"""

from pydantic import BaseModel, Field
from typing import Annotated


class StripeModel(BaseModel):
    """Model for the stripe checkout screen."""
    amount: Annotated[int, Field(ge=3)]

class PaymentUrlResponse(BaseModel):
    """Response model for a payment URL."""

    url: str = Field(..., description="Checkout URL for payment", example="https://checkout.stripe.com/c/pay/awdaoOiawhd1cXdwYHgl")

class StripeResponse(BaseModel):
    """JSON:API resource for the payment URL."""

    data: PaymentUrlResponse
