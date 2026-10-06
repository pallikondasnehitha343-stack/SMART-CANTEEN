from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order
from app.models.payment import Payment, PaymentStatus
from app.models.user import User
from app.schemas.payment import (
    PaymentInitiateRequest, PaymentVerifyRequest, PaymentWebhookRequest, PaymentResponse
)
from app.services.payment_service import PaymentService
from app.services.auth_service import get_current_user
from app.realtime.connection_manager import ws_manager

router = APIRouter(prefix="/payments", tags=["Payments & Idempotency"])

@router.post("/initiate", response_model=PaymentResponse)
def initiate_payment(
    req: PaymentInitiateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == req.order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        
    payment = PaymentService.initiate_payment(
        db=db,
        order=order,
        payment_method=req.payment_method,
        idempotency_key=req.idempotency_key
    )
    return payment

@router.post("/verify", response_model=PaymentResponse)
async def verify_payment(
    req: PaymentVerifyRequest,
    db: Session = Depends(get_db)
):
    payment, order = PaymentService.verify_payment(
        db=db,
        transaction_id=req.transaction_id,
        gateway_signature=req.gateway_signature,
        reported_status=req.status
    )
    
    if payment.status == PaymentStatus.SUCCESS:
        await ws_manager.broadcast_order_update(order.id, {"event": "PAYMENT_SUCCESS", "order_id": order.id})
        
    return payment

@router.post("/webhook", response_model=PaymentResponse)
async def payment_webhook(
    req: PaymentWebhookRequest,
    db: Session = Depends(get_db)
):
    payment, order = PaymentService.verify_payment(
        db=db,
        transaction_id=req.transaction_id,
        gateway_signature=req.signature,
        reported_status=req.status
    )
    return payment

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return payment
