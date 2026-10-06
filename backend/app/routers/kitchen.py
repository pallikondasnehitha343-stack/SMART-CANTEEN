from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order, OrderStatus
from app.models.queue import QueueEntry
from app.models.user import User, UserRole
from app.models.notification import Notification
from app.schemas.order import OrderResponse
from app.routers.orders import build_order_response
from app.services.auth_service import require_roles
from app.services.queue_service import QueueService
from app.realtime.connection_manager import ws_manager

router = APIRouter(prefix="/kitchen", tags=["Kitchen Display System (KDS)"])

@router.get("/orders", response_model=List[OrderResponse])
def get_kitchen_display_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STAFF, UserRole.ADMIN]))
):
    QueueService.recalculate_queue_priorities(db)
    active_statuses = [OrderStatus.QUEUED, OrderStatus.ACCEPTED, OrderStatus.PREPARING, OrderStatus.READY]
    orders = db.query(Order).filter(Order.status.in_(active_statuses)).order_by(Order.created_at.asc()).all()
    return [build_order_response(o, db) for o in orders]

@router.post("/orders/{order_id}/start-prep", response_model=OrderResponse)
async def start_preparation(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STAFF, UserRole.ADMIN]))
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order.status = OrderStatus.PREPARING
    
    # Update queue entry
    queue_entry = db.query(QueueEntry).filter(QueueEntry.order_id == order.id).first()
    if queue_entry:
        queue_entry.started_prep_at = datetime.utcnow()

    # Create notification for student
    notif = Notification(
        user_id=order.user_id,
        order_id=order.id,
        title="Kitchen Started Preparing Your Food!",
        message=f"Order {order.order_number} is now being actively prepared at {queue_entry.assigned_station if queue_entry else 'Counter'}.",
        notification_type="ORDER_PREPARING"
    )
    db.add(notif)
    db.commit()
    db.refresh(order)

    resp = build_order_response(order, db)
    await ws_manager.broadcast_order_update(order.id, resp.model_dump(mode="json"))
    return resp

@router.post("/orders/{order_id}/mark-ready", response_model=OrderResponse)
async def mark_order_ready(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STAFF, UserRole.ADMIN]))
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order.status = OrderStatus.READY
    order.actual_ready_time = datetime.utcnow()

    # Create push notification for student
    notif = Notification(
        user_id=order.user_id,
        order_id=order.id,
        title="Food Ready For Pickup!",
        message=f"Order {order.order_number} (#{order.token_number}) is HOT & READY! Please present your QR token at pickup counter.",
        notification_type="ORDER_READY"
    )
    db.add(notif)
    db.commit()
    db.refresh(order)

    resp = build_order_response(order, db)
    await ws_manager.broadcast_order_update(order.id, resp.model_dump(mode="json"))
    return resp
