from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class OperationalDashboardMetrics(BaseModel):
    active_orders_count: int
    queued_count: int
    preparing_count: int
    ready_count: int
    completed_today: int
    cancelled_today: int
    current_peak_status: str # NORMAL, BUSY, HIGH, CRITICAL
    kitchen_utilization_pct: float
    avg_eta_minutes: float
    avg_waiting_time_minutes: float
    total_revenue_today: float
    slot_congestion_alerts: int
    low_stock_items_count: int
    system_throughput_per_hour: float

class BottleneckAlert(BaseModel):
    id: int
    detected_at: datetime
    bottleneck_type: str
    severity: str
    active_orders_count: int
    avg_eta_minutes: float
    description: str
    recommended_action: Optional[str] = None

class DemandForecastItem(BaseModel):
    time_window: str # e.g. "Next 15 Min", "Next 30 Min", "Next 1 Hour"
    predicted_orders: int
    predicted_peak_level: str
    recommended_active_stations: int
    high_demand_categories: List[str]

class DemandForecastResponse(BaseModel):
    generated_at: datetime
    forecasts: List[DemandForecastItem]
    model_version: str
    evaluation_mae: float # Mean Absolute Error metric for scientific reporting
