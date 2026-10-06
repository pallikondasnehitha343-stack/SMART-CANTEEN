from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.config import settings
from app.models.order import Order, OrderStatus
from app.models.queue import QueueEntry
from app.models.pickup_slot import PickupSlot
from app.schemas.queue import QueueItemResponse, QueueSummaryResponse

class QueueService:
    @staticmethod
    def calculate_priority_score(
        entered_at: datetime,
        prep_complexity: float,
        pickup_slot: Optional[PickupSlot] = None
    ) -> tuple[float, float, float, float]:
        """
        Fair Aging Queue Score Formula:
        Priority = 100.0 + AgingBonus + UrgencyFactor - ComplexityPenalty
        
        As an order waits in queue, AgingBonus increases linearly (anti-starvation guarantee).
        """
        now = datetime.utcnow()
        waiting_time_minutes = max(0.0, (now - entered_at).total_seconds() / 60.0)
        
        # Anti-starvation aging bonus
        aging_bonus = waiting_time_minutes * settings.AGING_BONUS_PER_MINUTE
        
        # Urgency bonus if assigned a pickup slot
        urgency_score = 1.0
        if pickup_slot:
            # Slot end time proximity increases urgency
            urgency_score = 1.5
            
        complexity_penalty = max(0.5, prep_complexity)
        
        priority_score = round(
            100.0 + (aging_bonus * settings.WEIGHT_WAITING_TIME * 10) 
            + (urgency_score * settings.WEIGHT_DEADLINE_URGENCY * 20) 
            - (complexity_penalty * settings.WEIGHT_PREP_COMPLEXITY * 5),
            2
        )
        return priority_score, waiting_time_minutes, aging_bonus, complexity_penalty

    @classmethod
    def enqueue_order(cls, db: Session, order: Order) -> QueueEntry:
        """Add confirmed order to virtual queue"""
        # Check if already queued
        existing = db.query(QueueEntry).filter(QueueEntry.order_id == order.id).first()
        if existing:
            return existing
            
        # Compute avg complexity of order
        avg_complexity = 1.0
        if order.items:
            avg_complexity = sum(item.complexity_snapshot for item in order.items) / len(order.items)
            
        priority_score, waiting_time, aging_bonus, complexity_penalty = cls.calculate_priority_score(
            entered_at=datetime.utcnow(),
            prep_complexity=avg_complexity,
            pickup_slot=order.pickup_slot
        )
        
        # Determine assigned station
        station_id = (order.id % settings.DEFAULT_KITCHEN_ACTIVE_STATIONS) + 1
        assigned_station = f"Station-{station_id}"
        
        # Determine queue position count
        active_queued_count = db.query(QueueEntry).join(Order).filter(
            Order.status.in_([OrderStatus.QUEUED, OrderStatus.ACCEPTED])
        ).count()
        
        queue_entry = QueueEntry(
            order_id=order.id,
            queue_position=active_queued_count + 1,
            priority_score=priority_score,
            waiting_time_minutes=waiting_time,
            aging_bonus=aging_bonus,
            urgency_score=1.0,
            complexity_penalty=complexity_penalty,
            assigned_station=assigned_station,
            entered_queue_at=datetime.utcnow()
        )
        db.add(queue_entry)
        order.status = OrderStatus.QUEUED
        db.commit()
        db.refresh(queue_entry)
        
        # Recalculate ranking
        cls.recalculate_queue_priorities(db)
        return queue_entry

    @classmethod
    def recalculate_queue_priorities(cls, db: Session):
        """Re-evaluates priority scores with aging credits for all active queued orders"""
        active_entries = (
            db.query(QueueEntry)
            .join(Order)
            .filter(Order.status.in_([OrderStatus.QUEUED, OrderStatus.ACCEPTED]))
            .all()
        )
        
        for entry in active_entries:
            order = entry.order
            avg_complexity = 1.0
            if order.items:
                avg_complexity = sum(item.complexity_snapshot for item in order.items) / len(order.items)
                
            p_score, w_time, a_bonus, c_penalty = cls.calculate_priority_score(
                entered_at=entry.entered_queue_at,
                prep_complexity=avg_complexity,
                pickup_slot=order.pickup_slot
            )
            entry.priority_score = p_score
            entry.waiting_time_minutes = round(w_time, 1)
            entry.aging_bonus = round(a_bonus, 2)
            entry.complexity_penalty = round(c_penalty, 2)
            
        db.commit()
        
        # Sort and update dynamic queue positions (higher priority = earlier position)
        sorted_entries = sorted(active_entries, key=lambda e: e.priority_score, reverse=True)
        for idx, entry in enumerate(sorted_entries):
            entry.queue_position = idx + 1
        db.commit()

    @classmethod
    def get_queue_summary(cls, db: Session) -> QueueSummaryResponse:
        """Generate comprehensive live queue & kitchen workload summary"""
        cls.recalculate_queue_priorities(db)
        
        queued_count = db.query(Order).filter(Order.status == OrderStatus.QUEUED).count()
        preparing_count = db.query(Order).filter(Order.status == OrderStatus.PREPARING).count()
        ready_count = db.query(Order).filter(Order.status == OrderStatus.READY).count()
        total_active = queued_count + preparing_count
        
        # Calculate average waiting time
        active_entries = db.query(QueueEntry).join(Order).filter(
            Order.status.in_([OrderStatus.QUEUED, OrderStatus.PREPARING])
        ).all()
        
        avg_wait = 0.0
        if active_entries:
            avg_wait = round(sum(e.waiting_time_minutes for e in active_entries) / len(active_entries), 1)
            
        # Classify kitchen workload
        if total_active < settings.PEAK_BUSY_ACTIVE_ORDERS:
            workload = "NORMAL"
        elif total_active < settings.PEAK_HIGH_ACTIVE_ORDERS:
            workload = "BUSY"
        elif total_active < settings.PEAK_CRITICAL_ACTIVE_ORDERS:
            workload = "HIGH"
        else:
            workload = "CRITICAL"
            
        queue_items = []
        for entry in sorted(active_entries, key=lambda e: e.queue_position):
            order = entry.order
            items_str = ", ".join([f"{item.quantity}x {item.menu_item.name}" for item in order.items if item.menu_item])
            queue_items.append(QueueItemResponse(
                queue_id=entry.id,
                order_id=order.id,
                order_number=order.order_number,
                token_number=order.token_number,
                user_name=order.user.full_name if order.user else "Campus Student",
                status=order.status,
                queue_position=entry.queue_position,
                priority_score=entry.priority_score,
                waiting_time_minutes=entry.waiting_time_minutes,
                estimated_prep_time_minutes=order.estimated_prep_time_minutes,
                assigned_station=entry.assigned_station,
                entered_queue_at=entry.entered_queue_at,
                items_summary=items_str or "Standard Order"
            ))
            
        return QueueSummaryResponse(
            total_active_orders=total_active,
            orders_queued=queued_count,
            orders_preparing=preparing_count,
            orders_ready=ready_count,
            avg_waiting_time_minutes=avg_wait,
            current_kitchen_workload=workload,
            active_kitchen_stations=settings.DEFAULT_KITCHEN_ACTIVE_STATIONS,
            estimated_throughput_per_min=round(
                settings.DEFAULT_KITCHEN_ACTIVE_STATIONS * settings.KITCHEN_THROUGHPUT_PER_STATION_PER_MIN, 2
            ),
            queue_list=queue_items
        )
