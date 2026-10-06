from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.queue import QueueSummaryResponse
from app.services.queue_service import QueueService
from app.realtime.connection_manager import ws_manager

router = APIRouter(prefix="/queue", tags=["Virtual Queue & Aging"])

@router.get("/summary", response_model=QueueSummaryResponse)
def get_queue_summary(db: Session = Depends(get_db)):
    return QueueService.get_queue_summary(db)

@router.post("/recalculate", response_model=QueueSummaryResponse)
async def recalculate_queue(db: Session = Depends(get_db)):
    QueueService.recalculate_queue_priorities(db)
    summary = QueueService.get_queue_summary(db)
    await ws_manager.broadcast_queue_update(summary.model_dump(mode="json"))
    return summary
