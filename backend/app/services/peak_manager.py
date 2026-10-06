from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.config import settings
from app.models.order import Order, OrderStatus
from app.models.pickup_slot import PickupSlot, SlotStatus
from app.models.analytics import BottleneckEvent

class PeakManager:
    @classmethod
    def evaluate_peak_state(cls, db: Session) -> Dict[str, Any]:
        """
        Evaluates real-time canteen operational congestion using multi-signal telemetry:
        1. Active orders in queue & prep
        2. 10-minute order arrival velocity
        3. Pickup slot capacity saturation
        """
        active_orders_count = db.query(Order).filter(
            Order.status.in_([OrderStatus.QUEUED, OrderStatus.ACCEPTED, OrderStatus.PREPARING])
        ).count()
        
        ten_mins_ago = datetime.utcnow() - timedelta(minutes=10)
        recent_orders_count = db.query(Order).filter(Order.created_at >= ten_mins_ago).count()
        arrival_velocity_per_min = round(recent_orders_count / 10.0, 2)
        
        # Calculate pickup slot saturation
        slots = db.query(PickupSlot).filter(PickupSlot.is_active == True).all()
        total_capacity = sum(s.capacity for s in slots) if slots else 100
        total_booked = sum(s.booked_count for s in slots) if slots else 0
        slot_saturation_pct = round((total_booked / max(1, total_capacity)) * 100, 1)
        
        # Kitchen utilization estimate
        max_active_target = settings.DEFAULT_KITCHEN_ACTIVE_STATIONS * 8
        kitchen_utilization = min(100.0, round((active_orders_count / max(1, max_active_target)) * 100, 1))
        
        # Congestion classification
        if active_orders_count >= settings.PEAK_CRITICAL_ACTIVE_ORDERS or slot_saturation_pct >= 90.0:
            peak_status = "CRITICAL"
            recommendation = "Kitchen at maximum surge! Order intake throttled. Recommend pickup slots in next hour."
        elif active_orders_count >= settings.PEAK_HIGH_ACTIVE_ORDERS or slot_saturation_pct >= 75.0:
            peak_status = "HIGH"
            recommendation = "High lunchtime congestion. Expect +5 to 10 min prep delay. Select later pickup slots."
        elif active_orders_count >= settings.PEAK_BUSY_ACTIVE_ORDERS or slot_saturation_pct >= 50.0:
            peak_status = "BUSY"
            recommendation = "Moderate rush. Standard preparation times in effect."
        else:
            peak_status = "NORMAL"
            recommendation = "Optimal operational flow. Fast fulfillment available."
            
        return {
            "peak_status": peak_status,
            "active_orders_count": active_orders_count,
            "arrival_velocity_per_min": arrival_velocity_per_min,
            "slot_saturation_pct": slot_saturation_pct,
            "kitchen_utilization_pct": kitchen_utilization,
            "recommendation": recommendation,
            "timestamp": datetime.utcnow()
        }
