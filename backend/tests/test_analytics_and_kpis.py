from fastapi import status

def test_admin_metrics_dashboard(client, admin_auth_headers):
    res = client.get("/api/v1/admin/metrics", headers=admin_auth_headers)
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert "active_orders_count" in data
    assert "current_peak_status" in data
    assert "kitchen_utilization_pct" in data
    assert "avg_eta_minutes" in data
    assert "total_revenue_today" in data

def test_demand_forecast_predictions(client, admin_auth_headers):
    res = client.get("/api/v1/analytics/forecast", headers=admin_auth_headers)
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert "forecasts" in data
    assert len(data["forecasts"]) == 3
    assert data["evaluation_mae"] > 0
    assert "recommended_active_stations" in data["forecasts"][0]
