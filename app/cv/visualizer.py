import cv2
import numpy as np

from app.cv.tracker import TrackedObject
from app.cv.zone_checker import Zone, ZoneViolation

# Colour palette per class name (BGR)
_CLASS_COLORS: dict[str, tuple[int, int, int]] = {
    "person":  (0, 200, 0),
    "car":     (0, 120, 255),
    "truck":   (0, 80, 200),
    "default": (200, 200, 0),
}
_ZONE_COLOR       = (0, 0, 220)    # red for restricted zones
_VIOLATION_COLOR  = (0, 0, 255)    # bright red for violated zones
_FONT             = cv2.FONT_HERSHEY_SIMPLEX


def draw_frame(
    frame: np.ndarray,
    tracked_objects: list[TrackedObject],
    zones: list[Zone],
    violations: list[ZoneViolation],
) -> np.ndarray:
    """
    Return an annotated copy of the frame with:
    - Coloured bounding boxes + class label + confidence + track ID
    - Zone rectangles (red = normal, bright red + filled = violation)
    """
    out = frame.copy()
    violated_zone_ids = {v.zone.id for v in violations}

    # Draw zones first (underneath the boxes)
    for zone in zones:
        color = _VIOLATION_COLOR if zone.id in violated_zone_ids else _ZONE_COLOR
        x, y, w, h = zone.x, zone.y, zone.width, zone.height

        # Semi-transparent fill
        overlay = out.copy()
        cv2.rectangle(overlay, (x, y), (x + w, y + h), color, -1)
        cv2.addWeighted(overlay, 0.15, out, 0.85, 0, out)

        # Solid border
        cv2.rectangle(out, (x, y), (x + w, y + h), color, 2)
        cv2.putText(out, zone.name, (x + 4, y - 6), _FONT, 0.5, color, 1, cv2.LINE_AA)

    # Draw tracked objects
    for obj in tracked_objects:
        det = obj.detection
        x1 = int(det.x)
        y1 = int(det.y)
        x2 = int(det.x + det.width)
        y2 = int(det.y + det.height)

        color = _CLASS_COLORS.get(det.class_name, _CLASS_COLORS["default"])
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)

        label = f"#{obj.track_id} {det.class_name} {det.confidence:.0%}"
        (tw, th), _ = cv2.getTextSize(label, _FONT, 0.5, 1)
        cv2.rectangle(out, (x1, y1 - th - 6), (x1 + tw + 4, y1), color, -1)
        cv2.putText(out, label, (x1 + 2, y1 - 4), _FONT, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    # HUD — frame stats in top-right corner
    hud = f"Objects: {len(tracked_objects)}  Alerts: {len(violations)}"
    cv2.putText(out, hud, (10, 24), _FONT, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(out, hud, (10, 24), _FONT, 0.6, (0, 0, 0),       1, cv2.LINE_AA)

    return out


def encode_jpeg(frame: np.ndarray, quality: int = 80) -> bytes:
    """Encode numpy frame to JPEG bytes."""
    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return buf.tobytes()
