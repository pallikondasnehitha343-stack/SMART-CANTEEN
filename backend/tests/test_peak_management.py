from app.services.peak_manager import PeakManager
from app.models.pickup_slot import PickupSlot, SlotStatus

def test_peak_load_detection_and_telemetry(db_session):
    telemetry = PeakManager.evaluate_peak_state(db_session)
    assert telemetry["peak_status"] in ["NORMAL", "BUSY", "HIGH", "CRITICAL"]
    assert "active_orders_count" in telemetry
    assert "arrival_velocity_per_min" in telemetry
    assert "kitchen_utilization_pct" in telemetry
    assert "recommendation" in telemetry

def test_slot_capacity_saturation_transition(db_session):
    slot = db_session.query(PickupSlot).first()
    slot.capacity = 10
    slot.booked_count = 8 # 80% saturation -> BUSY
    
    from app.services.pickup_service import PickupService
    status = PickupService.update_slot_status(slot)
    assert status == SlotStatus.BUSY

    slot.booked_count = 10 # 100% -> FULL
    status = PickupService.update_slot_status(slot)
    assert status == SlotStatus.FULL
