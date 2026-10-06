from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.analytics import DemandForecastResponse, OperationalDashboardMetrics
from app.services.analytics_service import AnalyticsService
from app.services.ml_forecasting import DemandForecastingEngine
from app.services.auth_service import require_roles

router = APIRouter(prefix="/analytics", tags=["Analytics & Demand Forecasting"])

@router.get("/dashboard", response_model=OperationalDashboardMetrics)
def get_analytics_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.STAFF]))
):
    return AnalyticsService.get_operational_metrics(db)

@router.get("/forecast", response_model=DemandForecastResponse)
def get_demand_forecast(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.STAFF]))
):
    return DemandForecastingEngine.generate_forecast(db)
