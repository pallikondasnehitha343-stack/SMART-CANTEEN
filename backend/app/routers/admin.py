from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.analytics import OperationalDashboardMetrics, BottleneckAlert
from app.services.analytics_service import AnalyticsService
from app.services.auth_service import require_roles

router = APIRouter(prefix="/admin", tags=["Admin Operations & Bottleneck Monitoring"])

@router.get("/metrics", response_model=OperationalDashboardMetrics)
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.STAFF]))
):
    return AnalyticsService.get_operational_metrics(db)

@router.get("/bottlenecks", response_model=List[BottleneckAlert])
def get_operational_bottlenecks(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.STAFF]))
):
    return AnalyticsService.get_recent_bottlenecks(db)
