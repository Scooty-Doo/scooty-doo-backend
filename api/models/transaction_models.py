from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class TransactionAttributes(BaseModel):
    amount: Decimal = Field(..., max_digits=10, decimal_places=2)
    transaction_type: str
    transaction_description: Optional[str] = None
    trip_id: Optional[int] = None
    payment_method_id: Optional[int] = None
    meta_data: Optional[Dict] = None
    created_at: datetime
    updated_at: datetime

class TransactionResource(BaseModel):
    """JSON:API resource object for transactions."""
    id: int
    type: str = "transactions"
    attributes: TransactionAttributes

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_db_model(cls, transaction: Any) -> "TransactionResource":
        """Create a TransactionResource from a database model."""
        return cls(
            id=transaction.id,
            attributes=TransactionAttributes.model_validate(transaction)
        )