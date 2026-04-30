from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Camera(Base):
    __tablename__ = "cameras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    # webcam index (e.g. "0") or RTSP stream URL
    source: Mapped[str] = mapped_column(String(512), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships — back-populated from child tables
    detections: Mapped[list["Detection"]] = relationship(back_populates="camera")
    tracked_objects: Mapped[list["TrackedObject"]] = relationship(back_populates="camera")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="camera")
