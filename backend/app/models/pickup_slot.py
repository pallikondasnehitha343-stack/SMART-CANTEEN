import enum
from datetime import datetime, time
from sqlalchemy import Column, Integer, String, Enum, DateTime, Time, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class SlotStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"  # < 70% booked
    BUSY = "BUSY"            # 70% - 99% booked
    FULL = "FULL"            # 100% booked
    CLOSED = "CLOSED"        # past slot or manually closed

class PickupSlot(Base):
    __tablename__ = "pickup_slots"

    id = Column(Integer, primary_key=True, index=True)
    slot_label = Column(String(50), nullable=False) # e.g. "12:30 PM - 12:45 PM"
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    capacity = Column(Integer, default=25, nullable=False)
    booked_count = Column(Integer, default=0, nullable=False)
    status = Column(Enum(SlotStatus), default=SlotStatus.AVAILABLE, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    orders = relationship("Order", back_populates="pickup_slot")

    @property
    def remaining_capacity(self) -> int:
        return max(0, self.capacity - self.booked_count)

    @property
    def utilization_percentage(self) -> float:
        if self.capacity == 0:
            return 100.0
        return round((self.booked_count / self.capacity) * 100, 1)
