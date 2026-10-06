from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.pickup_slot import PickupSlot
from app.models.user import User, UserRole
from app.schemas.pickup import PickupSlotCreate, PickupSlotUpdate, PickupSlotResponse
from app.services.pickup_service import PickupService
from app.services.auth_service import require_roles

router = APIRouter(prefix="/pickup", tags=["Pickup Slots"])

@router.get("/slots", response_model=List[PickupSlotResponse])
def get_pickup_slots(db: Session = Depends(get_db)):
    slots = PickupService.get_all_slots(db)
    rec_slot = PickupService.get_recommended_slot(db)
    
    results = []
    for s in slots:
        resp = PickupSlotResponse(
            id=s.id,
            slot_label=s.slot_label,
            start_time=s.start_time.strftime("%H:%M") if hasattr(s.start_time, "strftime") else str(s.start_time),
            end_time=s.end_time.strftime("%H:%M") if hasattr(s.end_time, "strftime") else str(s.end_time),
            capacity=s.capacity,
            booked_count=s.booked_count,
            remaining_capacity=s.remaining_capacity,
            utilization_percentage=s.utilization_percentage,
            status=s.status,
            is_active=s.is_active,
            is_recommended=(rec_slot is not None and rec_slot.id == s.id)
        )
        results.append(resp)
    return results

@router.get("/slots/recommended", response_model=PickupSlotResponse)
def get_recommended_slot(db: Session = Depends(get_db)):
    slot = PickupService.get_recommended_slot(db)
    if not slot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No available pickup slots")
    return PickupSlotResponse(
        id=slot.id,
        slot_label=slot.slot_label,
        start_time=slot.start_time.strftime("%H:%M") if hasattr(slot.start_time, "strftime") else str(slot.start_time),
        end_time=slot.end_time.strftime("%H:%M") if hasattr(slot.end_time, "strftime") else str(slot.end_time),
        capacity=slot.capacity,
        booked_count=slot.booked_count,
        remaining_capacity=slot.remaining_capacity,
        utilization_percentage=slot.utilization_percentage,
        status=slot.status,
        is_active=slot.is_active,
        is_recommended=True
    )

@router.put("/slots/{slot_id}", response_model=PickupSlotResponse)
def update_slot(
    slot_id: int,
    slot_in: PickupSlotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.STAFF]))
):
    slot = db.query(PickupSlot).filter(PickupSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found")
        
    update_data = slot_in.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(slot, k, v)
        
    PickupService.update_slot_status(slot)
    db.commit()
    db.refresh(slot)
    return PickupSlotResponse(
        id=slot.id,
        slot_label=slot.slot_label,
        start_time=slot.start_time.strftime("%H:%M") if hasattr(slot.start_time, "strftime") else str(slot.start_time),
        end_time=slot.end_time.strftime("%H:%M") if hasattr(slot.end_time, "strftime") else str(slot.end_time),
        capacity=slot.capacity,
        booked_count=slot.booked_count,
        remaining_capacity=slot.remaining_capacity,
        utilization_percentage=slot.utilization_percentage,
        status=slot.status,
        is_active=slot.is_active,
        is_recommended=False
    )
