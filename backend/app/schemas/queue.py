from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.order import OrderStatus

class QueueItemResponse(BaseModel):
    queue_id: int
    order_id: int
    order_number: str
    token_number: str
    user_name: str
    status: OrderStatus
    queue_position: int
    priority_score: float
    waiting_time_minutes: float
    estimated_prep_time_minutes: int
    assigned_station: str
    entered_queue_at: datetime
    items_summary: str

    class Config:
        from_attributes = True

class QueueSummaryResponse(BaseModel):
    total_active_orders: int
    orders_queued: int
    orders_preparing: int
    orders_ready: int
    avg_waiting_time_minutes: float
    current_kitchen_workload: str # NORMAL, BUSY, HIGH, CRITICAL
    active_kitchen_stations: int
    estimated_throughput_per_min: float
    queue_list: List[QueueItemResponse] = []
