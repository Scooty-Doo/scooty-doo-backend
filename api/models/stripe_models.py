"""MOdule with models for OAuth2"""

from pydantic import BaseModel, Field
from typing import Annotated


class StripeModel(BaseModel):
    """Model for the stripe checkout screen."""
    amount: Annotated[int, Field(ge=3)]
