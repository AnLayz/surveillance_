from dataclasses import dataclass, field

from app.cv.detector import DetectionResult

# A track is dropped if unseen for this many consecutive frames
_MAX_MISSING_FRAMES = 10


@dataclass
class TrackedObject:
    """A detection with a persistent identity across frames."""
    track_id: int
    detection: DetectionResult
    missing_frames: int = 0   # frames since last matched detection


def _iou(a: tuple, b: tuple) -> float:
    """Intersection-over-Union for two (x1,y1,x2,y2) boxes."""
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
    if inter_area == 0:
        return 0.0

    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    return inter_area / (area_a + area_b - inter_area)


class Tracker:
    """
    IoU-based tracker: matches new detections to existing tracks by
    highest bounding-box overlap. New detections with no match get a
    fresh track_id. Tracks unseen for _MAX_MISSING_FRAMES are removed.
    """

    _IOU_THRESHOLD = 0.3   # minimum overlap to consider a match

    def __init__(self) -> None:
        self._tracks: dict[int, TrackedObject] = {}
        self._next_id: int = 1

    def update(self, detections: list[DetectionResult]) -> list[TrackedObject]:
        """
        Feed current-frame detections, get back list of TrackedObjects
        (each with a stable track_id).
        """
        # Mark all existing tracks as potentially missing
        for t in self._tracks.values():
            t.missing_frames += 1

        unmatched_detections = list(detections)

        # Try to match each detection to an existing track
        for det in detections:
            best_id, best_iou = None, self._IOU_THRESHOLD

            for tid, track in self._tracks.items():
                score = _iou(det.bbox_xyxy, track.detection.bbox_xyxy)
                if score > best_iou:
                    best_iou = score
                    best_id = tid

            if best_id is not None:
                # Update existing track with new detection
                self._tracks[best_id].detection = det
                self._tracks[best_id].missing_frames = 0
                unmatched_detections.remove(det)

        # Register unmatched detections as new tracks
        for det in unmatched_detections:
            self._tracks[self._next_id] = TrackedObject(
                track_id=self._next_id, detection=det
            )
            self._next_id += 1

        # Evict stale tracks
        self._tracks = {
            tid: t
            for tid, t in self._tracks.items()
            if t.missing_frames <= _MAX_MISSING_FRAMES
        }

        return list(self._tracks.values())

    def reset(self) -> None:
        self._tracks.clear()
        self._next_id = 1
