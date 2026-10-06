from fastapi import status
from app.models.menu_item import MenuItem

def test_qr_pickup_full_lifecycle_and_single_use_protection(client, student_auth_headers, staff_auth_headers, db_session):
    samosa = db_session.query(MenuItem).filter(MenuItem.name == "Crispy Samosa").first()
    
    # 1. Student creates order
    order_res = client.post("/api/v1/orders", json={"items": [{"menu_item_id": samosa.id, "quantity": 1}]}, headers=student_auth_headers)
    assert order_res.status_code == status.HTTP_201_CREATED
    order_data = order_res.json()
    order_id = order_data["id"]
    qr_token = order_data["pickup_qr_token"]
    assert qr_token is not None

    # 2. Premature scan: Staff scans while still QUEUED -> Must fail
    scan_premature = client.post("/api/v1/orders/verify-qr", json={"qr_token": qr_token}, headers=staff_auth_headers)
    assert scan_premature.status_code == status.HTTP_400_BAD_REQUEST
    assert "not READY" in scan_premature.json()["detail"]

    # 3. Kitchen marks order PREPARING -> READY
    client.post(f"/api/v1/kitchen/orders/{order_id}/start-prep", headers=staff_auth_headers)
    client.post(f"/api/v1/kitchen/orders/{order_id}/mark-ready", headers=staff_auth_headers)

    # 4. Legitimate QR scan at pickup counter -> Must SUCCEED
    scan_valid = client.post("/api/v1/orders/verify-qr", json={"qr_token": qr_token}, headers=staff_auth_headers)
    assert scan_valid.status_code == status.HTTP_200_OK
    assert scan_valid.json()["success"] is True
    assert scan_valid.json()["order_number"] == order_data["order_number"]

    # 5. Replay Attack: Student attempts to reuse the same QR token a second time -> Must FAIL with 409 Conflict
    scan_replay = client.post("/api/v1/orders/verify-qr", json={"qr_token": qr_token}, headers=staff_auth_headers)
    assert scan_replay.status_code == status.HTTP_409_CONFLICT
    assert "ALREADY BEEN USED" in scan_replay.json()["detail"]

def test_tampered_qr_token_rejected(client, staff_auth_headers):
    # Alter the HMAC signature portion of the token
    fake_token = "eyJvcmRlcl9pZCI6IDk5OSwgInVzZXJfaWQiOiAxfQ==.fake_tampered_hmac_signature_invalid"
    scan_res = client.post("/api/v1/orders/verify-qr", json={"qr_token": fake_token}, headers=staff_auth_headers)
    assert scan_res.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid QR token signature" in scan_res.json()["detail"]
