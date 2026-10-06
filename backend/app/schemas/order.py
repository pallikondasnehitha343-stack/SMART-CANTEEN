from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.order import OrderStatus
from app.schemas.pickup import PickupSlotResponse

class CartItemRequest(BaseModel):
    menu_item_id: int
    quantity: int = Field(..., gt=0, description="Quantity must be at least 1")

class OrderCreateRequest(BaseModel):
    items: List[CartItemRequest]
    pickup_slot_id: Optional[int] = None
    special_instructions: Optional[str] = None
    payment_method: Optional[str] = "CAMPUS_WALLET"
    idempotency_key: Optional[str] = None

class OrderItemResponse(BaseModel):
    id: int
    menu_item_id: int
    menu_item_name: str
    quantity: int
    unit_price: float
    total_price: float
    prep_time_snapshot: int

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    order_number: str
    token_number: str
    user_id: int
    user_name: Optional[str] = None
    campus_id: Optional[str] = None
    status: OrderStatus
    total_amount: float
    pickup_slot_id: Optional[int] = None
    pickup_slot: Optional[PickupSlotResponse] = None
    estimated_prep_time_minutes: int
    estimated_ready_time: Optional[datetime] = None
    actual_ready_time: Optional[datetime] = None
    picked_up_at: Optional[datetime] = None
    
    # Virtual Queue Details
    queue_position: Optional[int] = None
    orders_ahead: Optional[int] = 0
    kitchen_workload_level: Optional[str] = "NORMAL"
    
    # Cryptographic QR Token
    pickup_qr_token: Optional[str] = None
    is_qr_used: int = 0
    
    special_instructions: Optional[str] = None
    items: List[OrderItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    notes: Optional[str] = None

class OrderQRVerifyRequest(BaseModel):
    qr_token: str

class OrderQRVerifyResponse(BaseModel):
    success: bool
    message: str
    order_id: Optional[int] = None
    order_number: Optional[str] = None
    token_number: Optional[str] = None
    user_name: Optional[str] = None
    items_count: Optional[int] = None
    verified_at: Optional[datetime] = None
