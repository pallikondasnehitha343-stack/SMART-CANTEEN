from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.order import Order, OrderStatus
from app.models.menu_item import MenuItem
from app.models.pickup_slot import PickupSlot
from app.models.analytics import BottleneckEvent, HourlyKPI
from app.services.peak_manager import PeakManager
from app.schemas.analytics import OperationalDashboardMetrics, BottleneckAlert

class AnalyticsService:
    @classmethod
    def get_operational_metrics(cls, db: Session) -> OperationalDashboardMetrics:
        """Fetch comprehensive live operational KPIs for Admin and Kitchen management"""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        queued_count = db.query(Order).filter(Order.status == OrderStatus.QUEUED).count()
        preparing_count = db.query(Order).filter(Order.status == OrderStatus.PREPARING).count()
        ready_count = db.query(Order).filter(Order.status == OrderStatus.READY).count()
        active_count = queued_count + preparing_count
        
        completed_today = db.query(Order).filter(
            Order.status == OrderStatus.PICKED_UP,
            Order.created_at >= today_start
        ).count()
        
        cancelled_today = db.query(Order).filter(
            Order.status.in_([OrderStatus.CANCELLED, OrderStatus.REFUNDED]),
            Order.created_at >= today_start
        ).count()
        
        # Revenue today
        revenue_today = db.query(func.sum(Order.total_amount)).filter(
            Order.status == OrderStatus.PICKED_UP,
            Order.created_at >= today_start
        ).scalar() or 0.0
        
        # Average prep time
        active_orders = db.query(Order).filter(Order.status.in_([OrderStatus.QUEUED, OrderStatus.PREPARING])).all()
        avg_eta = (
            round(sum(o.estimated_prep_time_minutes for o in active_orders) / len(active_orders), 1)
            if active_orders else 8.0
        )
        
        # Low stock items (< 10)
        low_stock_count = db.query(MenuItem).filter(MenuItem.stock_quantity < 10).count()
        
        peak_telemetry = PeakManager.evaluate_peak_state(db)
        
        return OperationalDashboardMetrics(
            active_orders_count=active_count,
            queued_count=queued_count,
            preparing_count=preparing_count,
            ready_count=ready_count,
            completed_today=completed_today,
            cancelled_today=cancelled_today,
            current_peak_status=peak_telemetry["peak_status"],
            kitchen_utilization_pct=peak_telemetry["kitchen_utilization_pct"],
            avg_eta_minutes=avg_eta,
            avg_waiting_time_minutes=round(avg_eta * 0.65, 1),
            total_revenue_today=round(float(revenue_today), 2),
            slot_congestion_alerts=1 if peak_telemetry["slot_saturation_pct"] > 80 else 0,
            low_stock_items_count=low_stock_count,
            system_throughput_per_hour=round(peak_telemetry["arrival_velocity_per_min"] * 60.0, 1)
        )

    @classmethod
    def get_recent_bottlenecks(cls, db: Session) -> List[BottleneckAlert]:
        """Fetch logged operational bottleneck alarms"""
        events = db.query(BottleneckEvent).order_by(BottleneckEvent.detected_at.desc()).limit(10).all()
        return [
            BottleneckAlert(
                id=e.id,
                detected_at=e.detected_at,
                bottleneck_type=e.bottleneck_type,
                severity=e.severity,
                active_orders_count=e.active_orders_count,
                avg_eta_minutes=e.avg_eta_minutes,
                description=e.description,
                recommended_action=e.recommended_action
            )
            for e in events
        ]
