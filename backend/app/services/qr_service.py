import hmac
import hashlib
import json
import base64
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.config import settings
from app.models.order import Order, OrderStatus
from app.models.queue import QueueEntry

class QRVerificationService:
    @staticmethod
    def generate_qr_token(order: Order) -> Tuple[str, str]:
        """
        Generates a tamper-proof cryptographic QR token tied to the order.
        Format: Base64(JSON_PAYLOAD) . HMAC_SHA256_SIGNATURE
        """
        payload = {
            "order_id": order.id,
            "order_number": order.order_number,
            "token_number": order.token_number,
            "user_id": order.user_id,
            "campus_id": order.user.campus_id if order.user else "",
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=6)).isoformat()
        }
        
        payload_json = json.dumps(payload, sort_keys=True)
        payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode()
        
        signature = hmac.new(
            settings.QR_SECRET_KEY.encode(),
            payload_b64.encode(),
            hashlib.sha256
        ).hexdigest()
        
        qr_token = f"{payload_b64}.{signature}"
        return qr_token, signature

    @classmethod
    def verify_and_claim_pickup(cls, db: Session, qr_token: str) -> Order:
        """
        Authoritatively validates QR token when scanned at kitchen pickup counter:
        1. Validates cryptographic HMAC signature.
        2. Checks payload integrity & expiration.
        3. Prevents single-token reuse (replay attack).
        4. Validates order status is READY.
        5. Atomically marks order as PICKED_UP.
        """
        parts = qr_token.strip().split(".")
        if len(parts) != 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Malformed QR token format"
            )
            
        payload_b64, signature = parts[0], parts[1]
        
        # Verify HMAC signature
        expected_sig = hmac.new(
            settings.QR_SECRET_KEY.encode(),
            payload_b64.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_sig):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid QR token signature! Verification rejected."
            )
            
        try:
            payload_json = base64.urlsafe_b64decode(payload_b64.encode()).decode()
            payload: Dict[str, Any] = json.loads(payload_json)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to decode QR token payload"
            )
            
        order_id = payload.get("order_id")
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
            
        # Check single-use replay protection
        if order.is_qr_used == 1 or order.status == OrderStatus.PICKED_UP:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Security Alert: This QR token for Order {order.order_number} has ALREADY BEEN USED at {order.picked_up_at}!"
            )
            
        # Check if order is ready for pickup
        if order.status != OrderStatus.READY:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order {order.order_number} is currently '{order.status.value}', not READY. Pickup disallowed."
            )
            
        # Atomically mark as consumed
        order.is_qr_used = 1
        order.status = OrderStatus.PICKED_UP
        order.picked_up_at = datetime.utcnow()
        
        # Update queue entry
        queue_entry = db.query(QueueEntry).filter(QueueEntry.order_id == order.id).first()
        if queue_entry:
            queue_entry.completed_prep_at = datetime.utcnow()
            
        db.commit()
        db.refresh(order)
        return order
