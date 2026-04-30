from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    camera_id: Mapped[int] = mapped_column(ForeignKey("cameras.id"), nullable=False)
    tracked_object_id: Mapped[int] = mapped_column(
        ForeignKey("tracked_objects.id"), nullable=False
    )
    detection_id: Mapped[int | None] = mapped_column(
        ForeignKey("detections.id"), nullable=True
    )

    # Which zone triggered this alert
    zone_id: Mapped[str] = mapped_column(String(100), nullable=False)

    # e.g. "zone_intrusion", "loitering", "perimeter_breach"
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    camera: Mapped["Camera"] = relationship(back_populates="alerts")
    tracked_object: Mapped["TrackedObject"] = relationship(back_populates="alerts")
