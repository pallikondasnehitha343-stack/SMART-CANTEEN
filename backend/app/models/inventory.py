import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class StockChangeReason(str, enum.Enum):
    ORDER_RESERVATION = "ORDER_RESERVATION"
    ORDER_CANCELLATION = "ORDER_CANCELLATION"
    MANUAL_RESTOCK = "MANUAL_RESTOCK"
    WASTAGE_ADJUSTMENT = "WASTAGE_ADJUSTMENT"

class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    change_amount = Column(Integer, nullable=False) # e.g. -2 for reservation, +50 for restock
    previous_stock = Column(Integer, nullable=False)
    new_stock = Column(Integer, nullable=False)
    reason = Column(Enum(StockChangeReason), nullable=False)
    reference_id = Column(String(100), nullable=True) # e.g. order_number or restock_batch
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    menu_item = relationship("MenuItem", back_populates="inventory_logs")
