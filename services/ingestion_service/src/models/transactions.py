from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class MerchantModel(BaseModel):
    id: str
    name: str
    country: str = Field(..., min_length=2, max_length=2)


class PayerModel(BaseModel):
    account_id: str
    pan_last: str = Field(..., min_length=4, max_length=4)
    ip_address: Optional[str] = None
    device_id: Optional[str] = None


class TransactionModel(BaseModel):
    transaction_id: str
    timestamp: datetime
    channel: str
    amount: float
    currency: str = Field(..., min_length=3, max_length=3)
    merchant: MerchantModel
    payer: PayerModel

    @validator("amount")
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Transaction amount must be greater than zero")
        return v
