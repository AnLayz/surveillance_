import asyncio
import logging
from pathlib import Path

import cv2

from app.core.config import settings
from app.cv.detector import Detector
from app.cv.frame_store import frame_store
from app.cv.tracker import Tracker
from app.cv.visualizer import draw_frame, encode_jpeg
from app.cv.zone_checker import ZoneChecker
from app.database.session import AsyncSessionLocal
from app.services import alert_service, detection_service
from app.services.telegram_service import send_alert
from app.services import ims_service

logger = logging.getLogger(__name__)


class SurveillancePipeline:
    """
    Main processing loop:
      capture frame → detect → track → zone check → persist → alert
    Runs as a background asyncio task. Call start() from FastAPI lifespan
    or from a management script.
    """

    def __init__(self, camera_id: int, zone_file: str | Path) -> None:
        self.camera_id = camera_id
        self._detector = Detector()
        self._tracker = Tracker()
        self._zone_checker = ZoneChecker(zone_file)
        self._running = False
        self._task: asyncio.Task | None = None

    # ------------------------------------------------------------------
    # Public control API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Schedule the pipeline as a background asyncio task."""
        if self._task and not self._task.done():
            logger.warning("Pipeline already running")
            return
        self._running = True
        self._task = asyncio.create_task(self._run(), name="surveillance-pipeline")
        logger.info("Pipeline started (camera_id=%d)", self.camera_id)

    def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
        logger.info("Pipeline stop requested")

    # ------------------------------------------------------------------
    # Internal loop
    # ------------------------------------------------------------------

    async def _run(self) -> None:
        loop = asyncio.get_event_loop()
        source = settings.camera_source
        # Convert to int if it's a digit string (webcam index)
        if isinstance(source, str) and source.isdigit():
            source = int(source)

        cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
        if not cap.isOpened():
            logger.error("Cannot open video source: %s", source)
            return

        frame_number = 0
        logger.info("Capture started from source: %s", source)

        try:
            while self._running:
                # Blocking capture in a thread so we don't stall the event loop
                ret, frame = await loop.run_in_executor(None, cap.read)
                if not ret:
                    logger.info("Video source exhausted or disconnected")
                    break

                frame_number += 1

                # CPU-bound inference also in executor
                detections = await loop.run_in_executor(
                    None, self._detector.detect, frame
                )
                tracked_objects = self._tracker.update(detections)
                violations = self._zone_checker.check(tracked_objects)

                # Encode annotated frame and push to MJPEG stream buffer
                annotated = draw_frame(frame, tracked_objects, self._zone_checker.zones, violations)
                jpeg = encode_jpeg(annotated)
                frame_store.push(jpeg)

                # Persist everything inside a single DB transaction per frame
                async with AsyncSessionLocal() as db:
                    async with db.begin():
                        await self._persist_frame(
                            db, tracked_objects, violations, frame_number
                        )

                # ~30 fps cap — prevents spinning on a live webcam
                await asyncio.sleep(0.033)

        except asyncio.CancelledError:
            logger.info("Pipeline task cancelled")
        finally:
            cap.release()
            logger.info("Capture released")

    async def _persist_frame(self, db, tracked_objects, violations, frame_number):
        """Save detections + tracked objects + alerts for one frame."""

        # Deactivate objects that disappeared from this frame
        active_ids = {obj.track_id for obj in tracked_objects}
        await detection_service.deactivate_missing_objects(db, self.camera_id, active_ids)

        # Map tracker track_id → DB TrackedObject row
        db_objects: dict[int, object] = {}

        for obj in tracked_objects:
            det = obj.detection
            db_obj = await detection_service.get_or_create_tracked_object(
                db,
                camera_id=self.camera_id,
                track_id=obj.track_id,
                class_name=det.class_name,
            )
            db_objects[obj.track_id] = db_obj

            await detection_service.save_detection(
                db,
                camera_id=self.camera_id,
                tracked_object_id=db_obj.id,
                det=det,
                frame_number=frame_number,
            )

        # Fire alerts for zone violations (with cooldown)
        for violation in violations:
            db_obj = db_objects.get(violation.tracked_object.track_id)
            if db_obj:
                new_alert = await alert_service.maybe_create_alert(
                    db,
                    camera_id=self.camera_id,
                    tracked_object=db_obj,
                    zone=violation.zone,
                )
                if new_alert:
                    logger.warning("ALERT: %s", new_alert.message)
                    await send_alert(new_alert.message)
                    await ims_service.create_incident(
                        alert_id=new_alert.id,
                        camera_id=self.camera_id,
                        message=new_alert.message,
                    )
