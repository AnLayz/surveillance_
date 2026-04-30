from dataclasses import dataclass

import numpy as np
from ultralytics import YOLO

from app.core.config import settings


@dataclass
class DetectionResult:
    """Single object detected in one frame."""
    class_name: str
    confidence: float
    # Bounding box in pixel coords: top-left x,y + width, height
    x: float
    y: float
    width: float
    height: float

    @property
    def center(self) -> tuple[float, float]:
        return (self.x + self.width / 2, self.y + self.height / 2)

    @property
    def bbox_xyxy(self) -> tuple[float, float, float, float]:
        """(x1, y1, x2, y2) format — used for IoU calculation."""
        return (self.x, self.y, self.x + self.width, self.y + self.height)


class Detector:
    """Thin wrapper around YOLOv8 — load once, run on every frame."""

    def __init__(self) -> None:
        self._model = YOLO(settings.yolo_model_path)
        self._confidence = settings.confidence_threshold

    def detect(self, frame: np.ndarray) -> list[DetectionResult]:
        """Run inference on a single BGR frame, return filtered detections."""
        results = self._model(frame, conf=self._confidence, verbose=False)[0]
        detections: list[DetectionResult] = []

        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            detections.append(
                DetectionResult(
                    class_name=results.names[int(box.cls)],
                    confidence=float(box.conf),
                    x=x1,
                    y=y1,
                    width=x2 - x1,
                    height=y2 - y1,
                )
            )

        return detections
