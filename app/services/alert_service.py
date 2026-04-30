from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cv.zone_checker import Zone
from app.models.alert import Alert
from app.models.tracked_object import TrackedObject

# Minimum seconds between repeated alerts for the same object+zone
_ALERT_COOLDOWN_SECONDS = 30


async def maybe_create_alert(
    db: AsyncSession,
    camera_id: int,
    tracked_object: TrackedObject,
    zone: Zone,
    detection_id: int | None = None,
) -> Alert | None:
    """
    Create a zone-intrusion alert only if no alert for this
    (track, zone) pair was fired within the cooldown window.
    Returns the new Alert or None if suppressed.
    """
    cooldown_cutoff = datetime.now(timezone.utc) - timedelta(seconds=_ALERT_COOLDOWN_SECONDS)

    recent = await db.execute(
        select(Alert).where(
            Alert.tracked_object_id == tracked_object.id,
            Alert.zone_id == zone.id,
            Alert.triggered_at >= cooldown_cutoff,
        )
    )
    if recent.scalar_one_or_none() is not None:
        return None  # still inside cooldown window

    alert = Alert(
        camera_id=camera_id,
        tracked_object_id=tracked_object.id,
        detection_id=detection_id,
        zone_id=zone.id,
        alert_type="zone_intrusion",
        message=(
            f"{tracked_object.object_class.capitalize()} (track #{tracked_object.track_id}) "
            f"entered restricted zone '{zone.name}'"
        ),
    )
    db.add(alert)
    await db.flush()
    return alert


async def list_alerts(db: AsyncSession, limit: int = 100) -> list[Alert]:
    result = await db.execute(
        select(Alert).order_by(Alert.triggered_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def get_stats(db: AsyncSession) -> dict:
    from sqlalchemy import func
    from app.models.detection import Detection
    from app.models.tracked_object import TrackedObject as TO

    total_det = (await db.execute(select(func.count()).select_from(Detection))).scalar()
    total_alerts = (await db.execute(select(func.count()).select_from(Alert))).scalar()
    active_tracks = (
        await db.execute(
            select(func.count()).select_from(TO).where(TO.is_active == True)
        )
    ).scalar()

    return {
        "total_detections": total_det,
        "total_alerts": total_alerts,
        "active_tracked_objects": active_tracks,
    }
