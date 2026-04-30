# Import all models here so Base.metadata knows about every table
# when create_all() is called in main.py lifespan
from app.models.alert import Alert
from app.models.camera import Camera
from app.models.detection import Detection
from app.models.tracked_object import TrackedObject

__all__ = ["Camera", "Detection", "TrackedObject", "Alert"]
