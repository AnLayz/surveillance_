import json
from dataclasses import dataclass
from pathlib import Path

from app.cv.tracker import TrackedObject


@dataclass
class Zone:
    id: str
    name: str
    zone_type: str   # "restricted" | "monitored" | etc.
    x: int
    y: int
    width: int
    height: int

    def contains_point(self, px: float, py: float) -> bool:
        """True if point (px, py) is inside this rectangular zone."""
        return self.x <= px <= self.x + self.width and self.y <= py <= self.y + self.height

    def intersects_bbox(self, bx: float, by: float, bw: float, bh: float) -> bool:
        """True if the bounding box overlaps with this zone at all."""
        # Two rectangles do NOT overlap if one is to the side/above/below the other
        no_overlap = (
            bx > self.x + self.width
            or bx + bw < self.x
            or by > self.y + self.height
            or by + bh < self.y
        )
        return not no_overlap


@dataclass
class ZoneViolation:
    """Produced when a tracked object enters a restricted zone."""
    tracked_object: TrackedObject
    zone: Zone


class ZoneChecker:
    """
    Loads zone definitions from a JSON file and evaluates each tracked
    object against every zone on every frame.
    """

    def __init__(self, zone_file: str | Path) -> None:
        self._zones: list[Zone] = self._load_zones(zone_file)

    @staticmethod
    def _load_zones(path: str | Path) -> list[Zone]:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        zones = []
        for z in data.get("zones", []):
            coords = z["coordinates"]
            zones.append(
                Zone(
                    id=z["id"],
                    name=z["name"],
                    zone_type=z["type"],
                    x=coords["x"],
                    y=coords["y"],
                    width=coords["width"],
                    height=coords["height"],
                )
            )
        return zones

    @property
    def zones(self) -> list[Zone]:
        return self._zones

    def check(self, tracked_objects: list[TrackedObject]) -> list[ZoneViolation]:
        """
        Check all tracked objects against all zones.
        Returns a violation for every (object, restricted-zone) pair that overlaps.
        """
        violations: list[ZoneViolation] = []

        for obj in tracked_objects:
            det = obj.detection

            for zone in self._zones:
                if zone.zone_type != "restricted":
                    continue
                # Use center-point check — change to intersects_bbox for stricter coverage
                if zone.intersects_bbox(det.x, det.y, det.width, det.height):
                    violations.append(ZoneViolation(tracked_object=obj, zone=zone))

        return violations
