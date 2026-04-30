from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.cv.detector import DetectionResult
from app.models.detection import Detection
from app.models.tracked_object import TrackedObject


async def get_or_create_tracked_object(
    db: AsyncSession,
    camera_id: int,
    track_id: int,
    class_name: str,
) -> TrackedObject:
    """Return existing DB row for this track, or insert a new one."""
    result = await db.execute(
        select(TrackedObject).where(
            TrackedObject.camera_id == camera_id,
            TrackedObject.track_id == track_id,
            TrackedObject.is_active == True,
        )
    )
    obj = result.scalar_one_or_none()

    if obj is None:
        obj = TrackedObject(
            camera_id=camera_id,
            track_id=track_id,
            object_class=class_name,
        )
        db.add(obj)
        await db.flush()   # get the generated id without committing yet

    else:
        # Keep last_seen_at fresh
        obj.last_seen_at = datetime.now(timezone.utc)

    return obj


async def save_detection(
    db: AsyncSession,
    camera_id: int,
    tracked_object_id: int,
    det: DetectionResult,
    frame_number: int,
) -> Detection:
    detection = Detection(
        camera_id=camera_id,
        tracked_object_id=tracked_object_id,
        object_class=det.class_name,
        confidence=det.confidence,
        bbox_x=det.x,
        bbox_y=det.y,
        bbox_width=det.width,
        bbox_height=det.height,
        frame_number=frame_number,
    )
    db.add(detection)
    await db.flush()
    return detection


async def deactivate_missing_objects(
    db: AsyncSession,
    camera_id: int,
    active_track_ids: set[int],
) -> None:
    """Mark as inactive all tracked objects not present in the current frame."""
    stmt = (
        update(TrackedObject)
        .where(
            TrackedObject.camera_id == camera_id,
            TrackedObject.is_active == True,
        )
    )
    if active_track_ids:
        stmt = stmt.where(TrackedObject.track_id.notin_(active_track_ids))
    await db.execute(stmt.values(is_active=False))


async def list_detections(db: AsyncSession, limit: int = 100) -> list[Detection]:
    result = await db.execute(
        select(Detection).order_by(Detection.detected_at.desc()).limit(limit)
    )
    return list(result.scalars().all())
