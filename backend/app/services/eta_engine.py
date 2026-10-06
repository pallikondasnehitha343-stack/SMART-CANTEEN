from datetime import datetime, timedelta
from typing import List, Tuple
from sqlalchemy.orm import Session

from app.config import settings
from app.models.order import Order, OrderStatus
from app.models.menu_item import MenuItem

class DynamicETAEngine:
    @staticmethod
    def calculate_order_workload(order: Order) -> float:
        """Calculate workload points for an order based on item prep times, complexity, and quantities"""
        total_workload = 0.0
        for item in order.items:
            prep_time = item.prep_time_snapshot or 5
            complexity = item.complexity_snapshot or 1.0
            # Workload = prep_time * (1 + 0.5 * (quantity - 1)) * complexity
            item_load = prep_time * (1.0 + 0.4 * (item.quantity - 1)) * complexity
            total_workload += item_load
        return max(total_workload, 4.0)

    @classmethod
    def calculate_dynamic_eta(
        cls,
        db: Session,
        order: Order,
        active_stations: int = settings.DEFAULT_KITCHEN_ACTIVE_STATIONS
    ) -> Tuple[int, datetime, int, str]:
        """
        Calculates dynamic ETA taking into account:
        1. Current order intrinsic preparation complexity
        2. Cumulative workload of all preceding active orders in queue / preparing
        3. Kitchen active parallel throughput
        4. Operational buffer
        
        Returns:
            (estimated_prep_time_minutes, estimated_ready_time, orders_ahead, workload_level)
        """
        # Fetch active orders ahead of this order (QUEUED, ACCEPTED, PREPARING)
        active_statuses = [OrderStatus.QUEUED, OrderStatus.ACCEPTED, OrderStatus.PREPARING]
        preceding_orders = (
            db.query(Order)
            .filter(
                Order.status.in_(active_statuses),
                Order.id != order.id,
                Order.created_at <= order.created_at
            )
            .all()
        )
        
        orders_ahead = len(preceding_orders)
        
        # Calculate preceding queue workload
        cumulative_queue_workload = sum(
            cls.calculate_order_workload(prev_order) for prev_order in preceding_orders
        )
        
        # Intrinsic workload of this order
        current_order_workload = cls.calculate_order_workload(order)
        
        # Parallel kitchen capacity calculation
        effective_capacity = max(1, active_stations) * settings.KITCHEN_THROUGHPUT_PER_STATION_PER_MIN
        
        # Base queue delay in minutes
        queue_delay_minutes = cumulative_queue_workload / (effective_capacity * 10.0)
        
        # Estimated prep time for this order itself
        intrinsic_prep_minutes = max(3.0, current_order_workload / max(1.0, active_stations * 0.75))
        
        # Total dynamic ETA
        total_eta_minutes = int(
            round(queue_delay_minutes + intrinsic_prep_minutes + settings.BASE_TRANSITION_BUFFER_MINUTES)
        )
        total_eta_minutes = max(total_eta_minutes, 5) # Minimum 5 minutes
        
        # Workload classification
        if orders_ahead < settings.PEAK_BUSY_ACTIVE_ORDERS:
            workload_level = "NORMAL"
        elif orders_ahead < settings.PEAK_HIGH_ACTIVE_ORDERS:
            workload_level = "BUSY"
        elif orders_ahead < settings.PEAK_CRITICAL_ACTIVE_ORDERS:
            workload_level = "HIGH"
        else:
            workload_level = "CRITICAL"
            
        estimated_ready_time = datetime.utcnow() + timedelta(minutes=total_eta_minutes)
        return total_eta_minutes, estimated_ready_time, orders_ahead, workload_level
