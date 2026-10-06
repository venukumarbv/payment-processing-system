from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MerchantDetail(BaseModel):
    MerchantID: str
    MerchantName: str
    CountryCode: str
    IsActive: bool
    CreatedAt: datetime
    UpdatedAt: datetime


class PayerDetail(BaseModel):
    PayerAccountID: str
    PanLast4: str
    IPAddress: Optional[str] = None
    DeviceID: Optional[str] = None
    IsActive: bool
    CreatedAt: datetime
    UpdatedAt: datetime


class TransactionResponse(BaseModel):
    TransactionID: str
    TransactionTimestamp: datetime
    Channel: str
    Amount: float
    Currency: str
    StatusID: int
    # Nested models to provide ALL details
    merchant: MerchantDetail
    payer: PayerDetail


class TopMerchantResponse(BaseModel):
    MerchantName: str
    TotalVolume: float
