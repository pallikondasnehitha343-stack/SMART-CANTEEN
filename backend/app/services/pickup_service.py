from typing import List, Optional
from datetime import datetime, time
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.pickup_slot import PickupSlot, SlotStatus

class PickupService:
    @staticmethod
    def get_all_slots(db: Session) -> List[PickupSlot]:
        """Fetch all pickup slots and refresh their operational status"""
        slots = db.query(PickupSlot).filter(PickupSlot.is_active == True).order_by(PickupSlot.start_time).all()
        for slot in slots:
            PickupService.update_slot_status(slot)
        db.commit()
        return slots

    @staticmethod
    def update_slot_status(slot: PickupSlot) -> SlotStatus:
        """Update slot status based on booked count vs capacity"""
        if slot.booked_count >= slot.capacity:
            slot.status = SlotStatus.FULL
        elif slot.booked_count >= int(slot.capacity * 0.70):
            slot.status = SlotStatus.BUSY
        else:
            slot.status = SlotStatus.AVAILABLE
        return slot.status

    @staticmethod
    def reserve_slot(db: Session, slot_id: int) -> PickupSlot:
        """Atomically reserve a pickup capacity slot"""
        slot = db.query(PickupSlot).filter(PickupSlot.id == slot_id).with_for_update().first() if "sqlite" not in str(db.bind.url) else db.query(PickupSlot).filter(PickupSlot.id == slot_id).first()
        
        if not slot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pickup slot not found")
            
        if slot.booked_count >= slot.capacity:
            slot.status = SlotStatus.FULL
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected pickup slot is FULL. Please select another recommended slot."
            )
            
        slot.booked_count += 1
        PickupService.update_slot_status(slot)
        db.commit()
        db.refresh(slot)
        return slot

    @staticmethod
    def release_slot(db: Session, slot_id: Optional[int]):
        """Release booked slot capacity upon cancellation or refund"""
        if not slot_id:
            return
        slot = db.query(PickupSlot).filter(PickupSlot.id == slot_id).first()
        if slot and slot.booked_count > 0:
            slot.booked_count -= 1
            PickupService.update_slot_status(slot)
            db.commit()

    @staticmethod
    def get_recommended_slot(db: Session) -> Optional[PickupSlot]:
        """Find the earliest available slot with lowest congestion"""
        slots = db.query(PickupSlot).filter(
            PickupSlot.is_active == True,
            PickupSlot.status == SlotStatus.AVAILABLE
        ).order_by(PickupSlot.booked_count, PickupSlot.start_time).first()
        return slots
