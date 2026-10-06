from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from app.database import Base

class QueueEntry(Base):
    __tablename__ = "queue_entries"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    queue_position = Column(Integer, default=1, nullable=False, index=True)
    priority_score = Column(Float, default=100.0, nullable=False, index=True) # Higher = higher priority in prep
    
    # Aging parameters for anti-starvation
    waiting_time_minutes = Column(Float, default=0.0, nullable=False)
    aging_bonus = Column(Float, default=0.0, nullable=False)
    urgency_score = Column(Float, default=1.0, nullable=False)
    complexity_penalty = Column(Float, default=1.0, nullable=False)
    
    assigned_station = Column(String(50), default="Station-1", nullable=False)
    entered_queue_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_prep_at = Column(DateTime, nullable=True)
    completed_prep_at = Column(DateTime, nullable=True)

    # Relationships
    order = relationship("Order", back_populates="queue_entry")
