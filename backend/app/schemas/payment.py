from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.payment import PaymentStatus, PaymentMethod

class PaymentInitiateRequest(BaseModel):
    order_id: int
    payment_method: PaymentMethod = PaymentMethod.CAMPUS_WALLET
    idempotency_key: str

class PaymentVerifyRequest(BaseModel):
    transaction_id: str
    gateway_signature: str
    status: PaymentStatus = PaymentStatus.SUCCESS

class PaymentWebhookRequest(BaseModel):
    transaction_id: str
    order_id: int
    status: PaymentStatus
    signature: str
    event_timestamp: datetime

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    transaction_id: str
    idempotency_key: Optional[str] = None
    amount: float
    currency: str
    payment_method: PaymentMethod
    status: PaymentStatus
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
