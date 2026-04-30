from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services import detection_service

router = APIRouter(prefix="/detections", tags=["detections"])


@router.get("/")
async def list_detections(
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    detections = await detection_service.list_detections(db, limit=limit)
    return {
        "count": len(detections),
        "detections": [
            {
                "id": d.id,
                "camera_id": d.camera_id,
                "tracked_object_id": d.tracked_object_id,
                "object_class": d.object_class,
                "confidence": round(d.confidence, 3),
                "bbox": {
                    "x": d.bbox_x,
                    "y": d.bbox_y,
                    "width": d.bbox_width,
                    "height": d.bbox_height,
                },
                "frame_number": d.frame_number,
                "detected_at": d.detected_at,
            }
            for d in detections
        ],
    }
