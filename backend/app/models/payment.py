import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class PaymentStatus(str, enum.Enum):
    INITIATED = "INITIATED"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"

class PaymentMethod(str, enum.Enum):
    CAMPUS_WALLET = "CAMPUS_WALLET"
    UPI = "UPI"
    CREDIT_DEBIT_CARD = "CREDIT_DEBIT_CARD"
    NET_BANKING = "NET_BANKING"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    transaction_id = Column(String(100), unique=True, index=True, nullable=False)
    idempotency_key = Column(String(100), unique=True, index=True, nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.CAMPUS_WALLET, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.INITIATED, nullable=False)
    gateway_response = Column(Text, nullable=True)
    error_message = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    order = relationship("Order", back_populates="payment")
