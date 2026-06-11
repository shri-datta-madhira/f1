from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LiveTiming(Base):
    """Transient: one row per driver per lap, deleted once official results land."""

    __tablename__ = "live_timing"
    __table_args__ = (
        UniqueConstraint("session_id", "driver_id", "lap_number"),     # no duplicate poll rows
        Index("ix_live_timing_session_lap", "session_id", "lap_number"),  # trailing-window read
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"))
    lap_number: Mapped[int]
    position: Mapped[int]
    gap_to_leader_ms: Mapped[int | None]
    interval_ahead_ms: Mapped[int | None]
    last_lap_ms: Mapped[int | None]
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())