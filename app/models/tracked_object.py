from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class TrackedObject(Base):
    __tablename__ = "tracked_objects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    camera_id: Mapped[int] = mapped_column(ForeignKey("cameras.id"), nullable=False)

    # The ID assigned by the tracker (resets each session; DB id is permanent)
    track_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    object_class: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "person"

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    # False once the object leaves the frame for good
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    camera: Mapped["Camera"] = relationship(back_populates="tracked_objects")
    detections: Mapped[list["Detection"]] = relationship(back_populates="tracked_object")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="tracked_object")
