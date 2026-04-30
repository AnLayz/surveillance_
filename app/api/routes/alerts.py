from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services import alert_service

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/")
async def list_alerts(
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    alerts = await alert_service.list_alerts(db, limit=limit)
    return {
        "count": len(alerts),
        "alerts": [
            {
                "id": a.id,
                "camera_id": a.camera_id,
                "tracked_object_id": a.tracked_object_id,
                "zone_id": a.zone_id,
                "alert_type": a.alert_type,
                "message": a.message,
                "is_resolved": a.is_resolved,
                "triggered_at": a.triggered_at,
            }
            for a in alerts
        ],
    }
