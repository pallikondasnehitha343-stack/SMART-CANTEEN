from fastapi import status
from app.models.menu_item import MenuItem
from app.models.order import OrderStatus
from app.services.payment_service import PaymentService

def test_payment_idempotency_prevents_duplicate_charge(client, student_auth_headers, db_session):
    samosa = db_session.query(MenuItem).filter(MenuItem.name == "Crispy Samosa").first()
    order_res = client.post("/api/v1/orders", json={"items": [{"menu_item_id": samosa.id, "quantity": 1}]}, headers=student_auth_headers)
    order_id = order_res.json()["id"]

    idempotency_key = "IDEMP_TEST_UNIQUE_12345"
    payload = {
        "order_id": order_id,
        "payment_method": "CAMPUS_WALLET",
        "idempotency_key": idempotency_key
    }

    # First attempt
    res1 = client.post("/api/v1/payments/initiate", json=payload, headers=student_auth_headers)
    assert res1.status_code == status.HTTP_200_OK
    pay1 = res1.json()

    # Second attempt with exact same idempotency key (simulating double-click)
    res2 = client.post("/api/v1/payments/initiate", json=payload, headers=student_auth_headers)
    assert res2.status_code == status.HTTP_200_OK
    pay2 = res2.json()

    assert pay1["id"] == pay2["id"]
    assert pay1["transaction_id"] == pay2["transaction_id"], "Idempotency must return identical transaction"

def test_payment_failure_restores_stock(client, student_auth_headers, db_session):
    samosa = db_session.query(MenuItem).filter(MenuItem.name == "Crispy Samosa").first()
    initial_stock = samosa.stock_quantity # 5

    # Order 3 samosas -> stock becomes 2
    order_res = client.post("/api/v1/orders", json={"items": [{"menu_item_id": samosa.id, "quantity": 3}]}, headers=student_auth_headers)
    order_id = order_res.json()["id"]
    
    db_session.expire_all()
    samosa_after_order = db_session.query(MenuItem).filter(MenuItem.id == samosa.id).first()
    assert samosa_after_order.stock_quantity == initial_stock - 3

    # Initiate payment
    init_res = client.post(
        "/api/v1/payments/initiate",
        json={"order_id": order_id, "payment_method": "UPI", "idempotency_key": "IDEMP_FAIL_001"},
        headers=student_auth_headers
    )
    txn_id = init_res.json()["transaction_id"]

    # Verify with FAILED status
    sig = PaymentService.generate_signature(f"{txn_id}:90.0:FAILED")
    verify_res = client.post("/api/v1/payments/verify", json={
        "transaction_id": txn_id,
        "gateway_signature": sig,
        "status": "FAILED"
    })
    assert verify_res.status_code == status.HTTP_200_OK
    assert verify_res.json()["status"] == "FAILED"

    # Verify inventory was automatically restored
    db_session.expire_all()
    samosa_restored = db_session.query(MenuItem).filter(MenuItem.id == samosa.id).first()
    assert samosa_restored.stock_quantity == initial_stock, "Failed payment must restore reserved stock"
