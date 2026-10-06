from typing import Optional
from pydantic import BaseModel
from datetime import time, datetime
from app.models.pickup_slot import SlotStatus

class PickupSlotBase(BaseModel):
    slot_label: str
    start_time: time
    end_time: time
    capacity: int = 25

class PickupSlotCreate(PickupSlotBase):
    pass

class PickupSlotUpdate(BaseModel):
    capacity: Optional[int] = None
    status: Optional[SlotStatus] = None
    is_active: Optional[bool] = None

class PickupSlotResponse(BaseModel):
    id: int
    slot_label: str
    start_time: str
    end_time: str
    capacity: int
    booked_count: int
    remaining_capacity: int
    utilization_percentage: float
    status: SlotStatus
    is_active: bool
    is_recommended: bool = False

    class Config:
        from_attributes = True
