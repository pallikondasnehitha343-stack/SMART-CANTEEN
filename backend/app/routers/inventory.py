from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.inventory import InventoryLog
from app.models.menu_item import MenuItem
from app.models.user import User, UserRole
from app.schemas.inventory import (
    InventoryUpdateRequest, InventoryLogResponse, LowStockAlert
)
from app.services.inventory_service import InventoryService
from app.services.auth_service import require_roles

router = APIRouter(prefix="/inventory", tags=["Inventory & Concurrency"])

@router.get("/logs", response_model=List[InventoryLogResponse])
def get_inventory_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.STAFF]))
):
    logs = db.query(InventoryLog).order_by(InventoryLog.created_at.desc()).limit(100).all()
    results = []
    for log in logs:
        resp = InventoryLogResponse.model_validate(log)
        resp.menu_item_name = log.menu_item.name if log.menu_item else "Unknown Item"
        results.append(resp)
    return results

@router.get("/low-stock", response_model=List[LowStockAlert])
def get_low_stock_alerts(
    threshold: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.STAFF]))
):
    items = db.query(MenuItem).filter(MenuItem.stock_quantity <= threshold).all()
    return [
        LowStockAlert(
            menu_item_id=item.id,
            name=item.name,
            current_stock=item.stock_quantity,
            threshold=threshold
        )
        for item in items
    ]

@router.post("/update", response_model=InventoryLogResponse)
def update_inventory(
    req: InventoryUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.STAFF]))
):
    item = InventoryService.update_stock(
        db=db,
        menu_item_id=req.menu_item_id,
        change_amount=req.change_amount,
        reason=req.reason,
        notes=req.notes or f"Manual update by {current_user.full_name}"
    )
    latest_log = (
        db.query(InventoryLog)
        .filter(InventoryLog.menu_item_id == req.menu_item_id)
        .order_by(InventoryLog.created_at.desc())
        .first()
    )
    resp = InventoryLogResponse.model_validate(latest_log)
    resp.menu_item_name = item.name
    return resp
