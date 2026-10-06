from datetime import datetime, timedelta
from fastapi import status
from app.models.menu_item import MenuItem
from app.models.order import Order, OrderStatus
from app.models.queue import QueueEntry
from app.services.queue_service import QueueService

def test_order_creation_and_queue_placement(client, student_auth_headers, db_session):
    samosa = db_session.query(MenuItem).filter(MenuItem.name == "Crispy Samosa").first()
    
    payload = {
        "items": [{"menu_item_id": samosa.id, "quantity": 2}],
        "special_instructions": "Extra chutney"
    }
    response = client.post("/api/v1/orders", json=payload, headers=student_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] in ["CONFIRMED", "QUEUED"]
    assert data["estimated_prep_time_minutes"] >= 5
    assert data["queue_position"] == 1
    assert data["pickup_qr_token"] is not None

def test_fair_aging_anti_starvation_score_progression(db_session):
    """
    Validates mathematical guarantee:
    An older order waiting in queue MUST achieve a higher priority score than a newly arrived order.
    """
    past_time = datetime.utcnow() - timedelta(minutes=15)
    
    score_old, wait_old, aging_old, _ = QueueService.calculate_priority_score(
        entered_at=past_time,
        prep_complexity=1.0
    )
    
    score_new, wait_new, aging_new, _ = QueueService.calculate_priority_score(
        entered_at=datetime.utcnow(),
        prep_complexity=1.0
    )
    
    assert wait_old >= 14.5
    assert aging_old > aging_new
    assert score_old > score_new, "Older order must have higher priority score due to anti-starvation aging bonus"

def test_kitchen_workflow_kanban_transition(client, staff_auth_headers, student_auth_headers, db_session):
    samosa = db_session.query(MenuItem).filter(MenuItem.name == "Crispy Samosa").first()
    order_res = client.post("/api/v1/orders", json={"items": [{"menu_item_id": samosa.id, "quantity": 1}]}, headers=student_auth_headers)
    order_id = order_res.json()["id"]

    # 1. Staff starts preparation
    prep_res = client.post(f"/api/v1/kitchen/orders/{order_id}/start-prep", headers=staff_auth_headers)
    assert prep_res.status_code == status.HTTP_200_OK
    assert prep_res.json()["status"] == "PREPARING"

    # 2. Staff marks ready
    ready_res = client.post(f"/api/v1/kitchen/orders/{order_id}/mark-ready", headers=staff_auth_headers)
    assert ready_res.status_code == status.HTTP_200_OK
    assert ready_res.json()["status"] == "READY"
    assert ready_res.json()["actual_ready_time"] is not None
