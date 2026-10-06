from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.database import Base

class HourlyKPI(Base):
    __tablename__ = "hourly_kpis"

    id = Column(Integer, primary_key=True, index=True)
    recorded_hour = Column(DateTime, default=datetime.utcnow, index=True)
    total_orders = Column(Integer, default=0)
    completed_orders = Column(Integer, default=0)
    cancelled_orders = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    avg_waiting_time_minutes = Column(Float, default=0.0)
    avg_prep_time_minutes = Column(Float, default=0.0)
    avg_pickup_delay_minutes = Column(Float, default=0.0)
    peak_level = Column(String(20), default="NORMAL") # NORMAL, BUSY, HIGH, CRITICAL
    kitchen_utilization_pct = Column(Float, default=0.0)

class BottleneckEvent(Base):
    __tablename__ = "bottleneck_events"

    id = Column(Integer, primary_key=True, index=True)
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)
    bottleneck_type = Column(String(50), nullable=False) # e.g. "KITCHEN_OVERLOAD", "PICKUP_SLOT_CONGESTION", "STOCK_EXHAUSTION"
    severity = Column(String(20), default="WARNING") # INFO, WARNING, CRITICAL
    active_orders_count = Column(Integer, default=0)
    avg_eta_minutes = Column(Float, default=0.0)
    description = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=True)
