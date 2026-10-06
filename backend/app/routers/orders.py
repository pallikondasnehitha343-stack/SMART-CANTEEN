import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order, OrderItem, OrderStatus
from app.models.user import User, UserRole
from app.models.menu_item import MenuItem
from app.models.notification import Notification
from app.schemas.order import (
    OrderCreateRequest, OrderResponse, OrderItemResponse, OrderStatusUpdate,
    OrderQRVerifyRequest, OrderQRVerifyResponse
)
from app.schemas.pickup import PickupSlotResponse
from app.services.auth_service import get_current_user, require_roles
from app.services.inventory_service import InventoryService
from app.services.pickup_service import PickupService
from app.services.payment_service import PaymentService
from app.services.eta_engine import DynamicETAEngine
from app.services.queue_service import QueueService
from app.services.qr_service import QRVerificationService
from app.realtime.connection_manager import ws_manager

router = APIRouter(prefix="/orders", tags=["Orders & Live Tracking"])

def build_order_response(order: Order, db: Session) -> OrderResponse:
    eta_mins, ready_time, orders_ahead, workload_lvl = DynamicETAEngine.calculate_dynamic_eta(db, order)
    
    # Map items
    items_resp = []
    for item in order.items:
        items_resp.append(OrderItemResponse(
            id=item.id,
            menu_item_id=item.menu_item_id,
            menu_item_name=item.menu_item.name if item.menu_item else "Campus Meal",
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.total_price,
            prep_time_snapshot=item.prep_time_snapshot
        ))
        
    slot_resp = None
    if order.pickup_slot:
        s = order.pickup_slot
        slot_resp = PickupSlotResponse(
            id=s.id,
            slot_label=s.slot_label,
            start_time=s.start_time.strftime("%H:%M") if hasattr(s.start_time, "strftime") else str(s.start_time),
            end_time=s.end_time.strftime("%H:%M") if hasattr(s.end_time, "strftime") else str(s.end_time),
            capacity=s.capacity,
            booked_count=s.booked_count,
            remaining_capacity=s.remaining_capacity,
            utilization_percentage=s.utilization_percentage,
            status=s.status,
            is_active=s.is_active,
            is_recommended=False
        )

    queue_pos = order.queue_entry.queue_position if order.queue_entry else (orders_ahead + 1)

    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        token_number=order.token_number,
        user_id=order.user_id,
        user_name=order.user.full_name if order.user else "",
        campus_id=order.user.campus_id if order.user else "",
        status=order.status,
        total_amount=order.total_amount,
        pickup_slot_id=order.pickup_slot_id,
        pickup_slot=slot_resp,
        estimated_prep_time_minutes=eta_mins,
        estimated_ready_time=order.estimated_ready_time or ready_time,
        actual_ready_time=order.actual_ready_time,
        picked_up_at=order.picked_up_at,
        queue_position=queue_pos,
        orders_ahead=orders_ahead,
        kitchen_workload_level=workload_lvl,
        pickup_qr_token=order.pickup_qr_token,
        is_qr_used=order.is_qr_used,
        special_instructions=order.special_instructions,
        items=items_resp,
        created_at=order.created_at,
        updated_at=order.updated_at
    )

@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not order_in.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart cannot be empty")
        
    # Generate unique order number & token
    today_str = datetime.utcnow().strftime("%Y%m%d")
    daily_count = db.query(Order).filter(Order.created_at >= datetime.utcnow().date()).count() + 1
    order_number = f"ORD-{today_str}-{daily_count:04d}"
    token_number = f"#T-{daily_count:03d}"

    # Step 1: Transactional stock reservation (prevents race conditions)
    reserved_items = InventoryService.validate_and_reserve_stock(db, order_in.items, order_number)
    
    # Step 2: Pickup slot reservation
    if order_in.pickup_slot_id:
        PickupService.reserve_slot(db, order_in.pickup_slot_id)

    # Step 3: Compute total and create Order entity
    total_amount = sum(item.price * qty for item, qty in reserved_items)
    
    order = Order(
        order_number=order_number,
        token_number=token_number,
        user_id=current_user.id,
        pickup_slot_id=order_in.pickup_slot_id,
        status=OrderStatus.CONFIRMED,
        total_amount=round(total_amount, 2),
        special_instructions=order_in.special_instructions
    )
    db.add(order)
    db.flush()

    # Step 4: Add order items
    for menu_item, qty in reserved_items:
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            quantity=qty,
            unit_price=menu_item.price,
            total_price=round(menu_item.price * qty, 2),
            prep_time_snapshot=menu_item.prep_time_minutes,
            complexity_snapshot=menu_item.complexity_score
        )
        db.add(order_item)
    db.flush()

    # Step 5: Dynamic ETA calculation
    eta_mins, ready_time, _, _ = DynamicETAEngine.calculate_dynamic_eta(db, order)
    order.estimated_prep_time_minutes = eta_mins
    order.estimated_ready_time = ready_time

    # Step 6: Generate Cryptographic QR Pickup Token
    qr_token, qr_sig = QRVerificationService.generate_qr_token(order)
    order.pickup_qr_token = qr_token
    order.pickup_qr_signature = qr_sig
    db.commit()
    db.refresh(order)

    # Step 7: Enqueue into Virtual Queue
    QueueService.enqueue_order(db, order)

    # Step 8: Create user notification
    notif = Notification(
        user_id=current_user.id,
        order_id=order.id,
        title="Order Confirmed & Queued",
        message=f"Order {order.order_number} (#{order.token_number}) has been placed. Live ETA: {eta_mins} mins.",
        notification_type="ORDER_CONFIRMED"
    )
    db.add(notif)
    db.commit()

    resp = build_order_response(order, db)
    await ws_manager.broadcast_order_update(order.id, resp.model_dump(mode="json"))
    return resp

@router.get("/my", response_model=List[OrderResponse])
def get_my_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()
    return [build_order_response(o, db) for o in orders]

@router.get("/{order_id}", response_model=OrderResponse)
def get_order_by_id(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        
    if current_user.role == UserRole.STUDENT and order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this order")
        
    return build_order_response(order, db)

@router.post("/verify-qr", response_model=OrderQRVerifyResponse)
async def verify_pickup_qr(
    req: OrderQRVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STAFF, UserRole.ADMIN]))
):
    order = QRVerificationService.verify_and_claim_pickup(db, req.qr_token)
    
    # Notify student
    notif = Notification(
        user_id=order.user_id,
        order_id=order.id,
        title="Order Picked Up!",
        message=f"Order {order.order_number} (#{order.token_number}) has been verified and picked up. Enjoy your meal!",
        notification_type="ORDER_PICKED_UP"
    )
    db.add(notif)
    db.commit()

    resp = build_order_response(order, db)
    await ws_manager.broadcast_order_update(order.id, resp.model_dump(mode="json"))
    
    return OrderQRVerifyResponse(
        success=True,
        message="Pickup verified successfully! Meal delivered.",
        order_id=order.id,
        order_number=order.order_number,
        token_number=order.token_number,
        user_name=order.user.full_name if order.user else "Campus Student",
        items_count=len(order.items),
        verified_at=order.picked_up_at
    )

@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_in: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STAFF, UserRole.ADMIN]))
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order.status = status_in.status
    if status_in.status == OrderStatus.READY:
        order.actual_ready_time = datetime.utcnow()
        # Add ready notification
        notif = Notification(
            user_id=order.user_id,
            order_id=order.id,
            title="Your Food is READY!",
            message=f"Order {order.order_number} (#{order.token_number}) is ready for pickup at Counter. Show your QR token!",
            notification_type="ORDER_READY"
        )
        db.add(notif)
    elif status_in.status in [OrderStatus.CANCELLED, OrderStatus.REFUNDED]:
        InventoryService.restore_stock_on_cancellation(db, order)
        PickupService.release_slot(db, order.pickup_slot_id)

    db.commit()
    db.refresh(order)
    
    resp = build_order_response(order, db)
    await ws_manager.broadcast_order_update(order.id, resp.model_dump(mode="json"))
    return resp
