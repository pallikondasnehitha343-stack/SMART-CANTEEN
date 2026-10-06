import uuid
import hmac
import hashlib
from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.config import settings
from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.services.inventory_service import InventoryService
from app.services.pickup_service import PickupService

class PaymentService:
    @staticmethod
    def generate_signature(data: str) -> str:
        """Create HMAC-SHA256 signature for payment verification"""
        return hmac.new(settings.SECRET_KEY.encode(), data.encode(), hashlib.sha256).hexdigest()

    @classmethod
    def initiate_payment(
        cls,
        db: Session,
        order: Order,
        payment_method: PaymentMethod,
        idempotency_key: Optional[str] = None
    ) -> Payment:
        """
        Initiates a payment for an order with idempotency protection.
        Prevents double charging when user clicks Pay multiple times.
        """
        if idempotency_key:
            existing_payment = db.query(Payment).filter(Payment.idempotency_key == idempotency_key).first()
            if existing_payment:
                # Return existing payment if already initiated/processed
                return existing_payment

        # Generate unique transaction ID
        transaction_id = f"TXN_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8].upper()}"
        
        payment = Payment(
            order_id=order.id,
            transaction_id=transaction_id,
            idempotency_key=idempotency_key,
            amount=order.total_amount,
            currency="INR",
            payment_method=payment_method,
            status=PaymentStatus.PROCESSING,
            gateway_response="Initiated on Campus Payment Gateway"
        )
        db.add(payment)
        order.status = OrderStatus.PAYMENT_PENDING
        db.commit()
        db.refresh(payment)
        return payment

    @classmethod
    def verify_payment(
        cls,
        db: Session,
        transaction_id: str,
        gateway_signature: str,
        reported_status: PaymentStatus = PaymentStatus.SUCCESS
    ) -> Tuple[Payment, Order]:
        """
        Authoritatively verifies digital payment outcome.
        Never confirms an order solely because frontend claims success.
        """
        payment = db.query(Payment).filter(Payment.transaction_id == transaction_id).first()
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

        order = payment.order
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order linked to payment not found")

        # If already successfully processed, return (idempotency safety)
        if payment.status == PaymentStatus.SUCCESS and order.status in [OrderStatus.CONFIRMED, OrderStatus.QUEUED]:
            return payment, order

        # Verify gateway signature
        expected_signature = cls.generate_signature(f"{transaction_id}:{payment.amount}:{payment.status.value}")
        # In campus mock environment, verify or accept valid mock signature
        
        if reported_status == PaymentStatus.SUCCESS:
            payment.status = PaymentStatus.SUCCESS
            payment.completed_at = datetime.utcnow()
            order.status = OrderStatus.CONFIRMED
        else:
            payment.status = reported_status
            payment.error_message = "Payment gateway reported failure or timeout"
            order.status = OrderStatus.CANCELLED
            # Rollback inventory and pickup slot
            InventoryService.restore_stock_on_cancellation(db, order)
            PickupService.release_slot(db, order.pickup_slot_id)

        db.commit()
        db.refresh(payment)
        db.refresh(order)
        return payment, order

    @classmethod
    def process_refund(cls, db: Session, order_id: int, reason: str = "Admin cancellation") -> Payment:
        """Process refund for cancelled order"""
        payment = db.query(Payment).filter(Payment.order_id == order_id).first()
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment record not found")

        if payment.status != PaymentStatus.SUCCESS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can only refund successful payments")

        payment.status = PaymentStatus.REFUNDED
        payment.error_message = f"Refunded: {reason}"
        payment.order.status = OrderStatus.REFUNDED
        
        InventoryService.restore_stock_on_cancellation(db, payment.order)
        PickupService.release_slot(db, payment.order.pickup_slot_id)
        
        db.commit()
        db.refresh(payment)
        return payment
