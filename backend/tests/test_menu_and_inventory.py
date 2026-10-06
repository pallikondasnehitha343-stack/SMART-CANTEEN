from fastapi import status
from app.models.menu_item import MenuItem

def test_get_menu_items(client):
    response = client.get("/api/v1/menu/items")
    assert response.status_code == status.HTTP_200_OK
    items = response.json()
    assert len(items) >= 2
    assert items[0]["name"] in ["Crispy Samosa", "Masala Dosa"]

def test_inventory_manual_restock(client, staff_auth_headers, db_session):
    item = db_session.query(MenuItem).filter(MenuItem.name == "Crispy Samosa").first()
    initial_stock = item.stock_quantity
    
    payload = {
        "menu_item_id": item.id,
        "change_amount": 25,
        "reason": "MANUAL_RESTOCK",
        "notes": "Morning fresh batch"
    }
    response = client.post("/api/v1/inventory/update", json=payload, headers=staff_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["new_stock"] == initial_stock + 25
    assert data["previous_stock"] == initial_stock

def test_low_stock_alerts(client, staff_auth_headers):
    response = client.get("/api/v1/inventory/low-stock?threshold=10", headers=staff_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    alerts = response.json()
    assert any(a["name"] == "Crispy Samosa" for a in alerts)
