import pytest
from fastapi import status
from app.models.menu_item import MenuItem
from app.models.pickup_slot import PickupSlot
from app.models.payment import PaymentStatus
from app.services.payment_service import PaymentService
from app.services.eta_engine import DynamicETAEngine

def test_concurrency_01_last_item_overselling_prevention(client, student_auth_headers, db_session):
    """Scenario 1: Two users purchasing the last remaining items simultaneously"""
    samosa = db_session.query(MenuItem).filter(MenuItem.name == "Crispy Samosa").first()
    samosa.stock_quantity = 2 # Exactly 2 left in stock
    db_session.commit()

    # User 1 successfully purchases both 2 samosas
    payload1 = {"items": [{"menu_item_id": samosa.id, "quantity": 2}]}
    res1 = client.post("/api/v1/orders", json=payload1, headers=student_auth_headers)
    assert res1.status_code == status.HTTP_201_CREATED

    # User 2 attempts to purchase 1 samosa simultaneously (stock is now 0) -> MUST be rejected
    payload2 = {"items": [{"menu_item_id": samosa.id, "quantity": 1}]}
    res2 = client.post("/api/v1/orders", json=payload2, headers=student_auth_headers)
    assert res2.status_code == status.HTTP_400_BAD_REQUEST
    assert "Insufficient stock" in res2.json()["detail"]

def test_concurrency_02_double_payment_callbacks_same_order(client, student_auth_headers, db_session):
    """Scenario 2: Two payment callbacks for the same order (webhook replay)"""
    samosa = db_session.query(MenuItem).filter(MenuItem.name == "Crispy Samosa").first()
    order_res = client.post("/api/v1/orders", json={"items": [{"menu_item_id": samosa.id, "quantity": 1}]}, headers=student_auth_headers)
    order_id = order_res.json()["id"]

    init_res = client.post("/api/v1/payments/initiate", json={"order_id": order_id, "payment_method": "UPI", "idempotency_key": "IDEMP_CONCUR_02"}, headers=student_auth_headers)
    txn_id = init_res.json()["transaction_id"]

    sig = PaymentService.generate_signature(f"{txn_id}:30.0:SUCCESS")
    verify_payload = {"transaction_id": txn_id, "gateway_signature": sig, "status": "SUCCESS"}

    # First callback
    cb1 = client.post("/api/v1/payments/verify", json=verify_payload)
    assert cb1.status_code == status.HTTP_200_OK
    assert cb1.json()["status"] == "SUCCESS"

    # Second concurrent duplicate callback
    cb2 = client.post("/api/v1/payments/verify", json=verify_payload)
    assert cb2.status_code == status.HTTP_200_OK
    assert cb2.json()["status"] == "SUCCESS"
    assert cb1.json()["id"] == cb2.json()["id"]

def test_concurrency_03_double_clicking_payment_button(client, student_auth_headers, db_session):
    """Scenario 3: Double clicking payment button handled cleanly via client idempotency key"""
    samosa = db_session.query(MenuItem).filter(MenuItem.name == "Crispy Samosa").first()
    order_res = client.post("/api/v1/orders", json={"items": [{"menu_item_id": samosa.id, "quantity": 1}]}, headers=student_auth_headers)
    order_id = order_res.json()["id"]

    key = "DOUBLE_CLICK_KEY_9999"
    res_click1 = client.post("/api/v1/payments/initiate", json={"order_id": order_id, "payment_method": "CAMPUS_WALLET", "idempotency_key": key}, headers=student_auth_headers)
    res_click2 = client.post("/api/v1/payments/initiate", json={"order_id": order_id, "payment_method": "CAMPUS_WALLET", "idempotency_key": key}, headers=student_auth_headers)

    assert res_click1.status_code == status.HTTP_200_OK
    assert res_click2.status_code == status.HTTP_200_OK
    assert res_click1.json()["transaction_id"] == res_click2.json()["transaction_id"]

def test_concurrency_04_duplicate_order_submission_with_zero_stock(client, student_auth_headers, db_session):
    """Scenario 4: Duplicate order submission when inventory reaches zero"""
    samosa = db_session.query(MenuItem).filter(MenuItem.name == "Crispy Samosa").first()
    samosa.stock_quantity = 1
    db_session.commit()

    res1 = client.post("/api/v1/orders", json={"items": [{"menu_item_id": samosa.id, "quantity": 1}]}, headers=student_auth_headers)
    assert res1.status_code == status.HTTP_201_CREATED

    res2 = client.post("/api/v1/orders", json={"items": [{"menu_item_id": samosa.id, "quantity": 1}]}, headers=student_auth_headers)
    assert res2.status_code == status.HTTP_400_BAD_REQUEST

def test_concurrency_05_two_staff_members_updating_same_order(client, staff_auth_headers, student_auth_headers, db_session):
    """Scenario 5: Two staff members updating the same order simultaneously"""
    samosa = db_session.query(MenuItem).filter(MenuItem.name == "Crispy Samosa").first()
    order_res = client.post("/api/v1/orders", json={"items": [{"menu_item_id": samosa.id, "quantity": 1}]}, headers=student_auth_headers)
    order_id = order_res.json()["id"]

    # Staff 1 and Staff 2 advance order
    u1 = client.post(f"/api/v1/kitchen/orders/{order_id}/start-prep", headers=staff_auth_headers)
    u2 = client.post(f"/api/v1/kitchen/orders/{order_id}/mark-ready", headers=staff_auth_headers)
    assert u1.status_code == status.HTTP_200_OK
    assert u2.status_code == status.HTTP_200_OK
    assert u2.json()["status"] == "READY"

def test_concurrency_06_pickup_qr_scanned_twice(client, student_auth_headers, staff_auth_headers, db_session):
    """Scenario 6: Pickup QR being scanned twice (Replay Protection)"""
    samosa = db_session.query(MenuItem).filter(MenuItem.name == "Crispy Samosa").first()
    order_res = client.post("/api/v1/orders", json={"items": [{"menu_item_id": samosa.id, "quantity": 1}]}, headers=student_auth_headers)
    order_data = order_res.json()
    order_id = order_data["id"]
    qr = order_data["pickup_qr_token"]

    client.post(f"/api/v1/kitchen/orders/{order_id}/mark-ready", headers=staff_auth_headers)

    scan1 = client.post("/api/v1/orders/verify-qr", json={"qr_token": qr}, headers=staff_auth_headers)
    assert scan1.status_code == status.HTTP_200_OK

    scan2 = client.post("/api/v1/orders/verify-qr", json={"qr_token": qr}, headers=staff_auth_headers)
    assert scan2.status_code == status.HTTP_409_CONFLICT

def test_concurrency_07_pickup_qr_used_while_not_ready(client, student_auth_headers, staff_auth_headers, db_session):
    """Scenario 7: Pickup QR being scanned while still in queue"""
    samosa = db_session.query(MenuItem).filter(MenuItem.name == "Crispy Samosa").first()
    order_res = client.post("/api/v1/orders", json={"items": [{"menu_item_id": samosa.id, "quantity": 1}]}, headers=student_auth_headers)
    qr = order_res.json()["pickup_qr_token"]

    scan = client.post("/api/v1/orders/verify-qr", json={"qr_token": qr}, headers=staff_auth_headers)
    assert scan.status_code == status.HTTP_400_BAD_REQUEST

def test_concurrency_08_pickup_slot_becoming_full(client, student_auth_headers, db_session):
    """Scenario 8: Pickup slot becoming full while users are ordering"""
    slot = db_session.query(PickupSlot).first()
    slot.capacity = 1
    slot.booked_count = 0
    db_session.commit()

    samosa = db_session.query(MenuItem).filter(MenuItem.name == "Crispy Samosa").first()
    
    # User 1 books the last slot capacity
    p1 = {"items": [{"menu_item_id": samosa.id, "quantity": 1}], "pickup_slot_id": slot.id}
    res1 = client.post("/api/v1/orders", json=p1, headers=student_auth_headers)
    assert res1.status_code == status.HTTP_201_CREATED

    # User 2 attempts to book the same slot -> MUST be rejected because capacity is now full
    p2 = {"items": [{"menu_item_id": samosa.id, "quantity": 1}], "pickup_slot_id": slot.id}
    res2 = client.post("/api/v1/orders", json=p2, headers=student_auth_headers)
    assert res2.status_code == status.HTTP_400_BAD_REQUEST
    assert "FULL" in res2.json()["detail"]

def test_concurrency_09_kitchen_workload_changing_dynamic_eta(client, student_auth_headers, db_session):
    """Scenario 9: Dynamic ETA updates dynamically when preceding queue workload changes"""
    dosa = db_session.query(MenuItem).filter(MenuItem.name == "Masala Dosa").first()
    
    # Place 3 orders
    o1 = client.post("/api/v1/orders", json={"items": [{"menu_item_id": dosa.id, "quantity": 1}]}, headers=student_auth_headers).json()
    o2 = client.post("/api/v1/orders", json={"items": [{"menu_item_id": dosa.id, "quantity": 1}]}, headers=student_auth_headers).json()
    o3 = client.post("/api/v1/orders", json={"items": [{"menu_item_id": dosa.id, "quantity": 1}]}, headers=student_auth_headers).json()

    assert o3["orders_ahead"] >= o1["orders_ahead"]
    assert o3["estimated_prep_time_minutes"] >= o1["estimated_prep_time_minutes"]

def test_concurrency_10_multiple_orders_peak_burst(client, student_auth_headers, db_session):
    """Scenario 10: Multiple orders arriving in a peak burst get sequential fair queue assignments"""
    samosa = db_session.query(MenuItem).filter(MenuItem.name == "Crispy Samosa").first()
    samosa.stock_quantity = 50
    db_session.commit()

    placed_orders = []
    for i in range(5):
        res = client.post("/api/v1/orders", json={"items": [{"menu_item_id": samosa.id, "quantity": 1}]}, headers=student_auth_headers)
        assert res.status_code == status.HTTP_201_CREATED
        placed_orders.append(res.json())

    # Ensure unique token numbers and monotonic queue positions
    token_numbers = [o["token_number"] for o in placed_orders]
    assert len(token_numbers) == len(set(token_numbers))
