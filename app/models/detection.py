from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Detection(Base):
    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    camera_id: Mapped[int] = mapped_column(ForeignKey("cameras.id"), nullable=False)
    tracked_object_id: Mapped[int | None] = mapped_column(
        ForeignKey("tracked_objects.id"), nullable=True
    )

    object_class: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    # Bounding box in pixel coordinates (top-left origin)
    bbox_x: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_y: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_width: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_height: Mapped[float] = mapped_column(Float, nullable=False)

    frame_number: Mapped[int] = mapped_column(Integer, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    camera: Mapped["Camera"] = relationship(back_populates="detections")
    tracked_object: Mapped["TrackedObject | None"] = relationship(back_populates="detections")
