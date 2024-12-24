from datetime import datetime
from decimal import Decimal
from typing import Any, Optional, Literal
from api.models.models import JsonApiLinks
from pydantic import BaseModel, ConfigDict, Field


class TransactionAttributes(BaseModel):
    """Attributes for a transaction."""
    amount: Decimal
    transaction_type: str
    transaction_description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class TransactionResourceMinimal(BaseModel):
    """JSON:API resource object for transactions without relationships."""
    id: str
    type: str = "transactions"
    attributes: TransactionAttributes
    links: Optional[JsonApiLinks] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_db_model(cls, transaction: Any, request_url: str) -> "TransactionResourceMinimal":
        """Create a TransactionResource from a database model."""
        return cls(
            id=str(transaction.id),
            attributes=TransactionAttributes.model_validate(transaction),
            links=JsonApiLinks(self_link=request_url)
        )

class TransactionGetRequestParams(BaseModel):
    """Model for getting a transaction"""
    # Pagination defaults to 100 transactions per page
    limit: int = Field(100, gt=0)
    offset: int = Field(0, ge=0)
    
    # Sorting
    order_by: Literal["created_at", "updated_at", "amount", "transaction_type"] = "created_at"
    order_direction: Literal["asc", "desc"] = "desc"

    amount_gt: Optional[Decimal] = None
    amount_lt: Optional[Decimal] = None
    transaction_type: Optional[str] = None
    created_at_gt: Optional[datetime] = None
    created_at_lt: Optional[datetime] = None
    updated_at_gt: Optional[datetime] = None
    updated_at_lt: Optional[datetime] = None