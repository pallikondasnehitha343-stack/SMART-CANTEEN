from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from app.models.inventory import StockChangeReason

class InventoryUpdateRequest(BaseModel):
    menu_item_id: int
    change_amount: int # +ve for restock, -ve for adjustment
    reason: StockChangeReason = StockChangeReason.MANUAL_RESTOCK
    notes: Optional[str] = None

class InventoryLogResponse(BaseModel):
    id: int
    menu_item_id: int
    menu_item_name: Optional[str] = None
    change_amount: int
    previous_stock: int
    new_stock: int
    reason: StockChangeReason
    reference_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class LowStockAlert(BaseModel):
    menu_item_id: int
    name: str
    current_stock: int
    threshold: int = 10
