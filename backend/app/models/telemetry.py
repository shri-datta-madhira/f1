from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Lap(Base):
    __tablename__ = "laps"
    __table_args__ = (UniqueConstraint("session_id", "driver_id", "lap_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"))
    lap_number: Mapped[int]
    lap_duration: Mapped[float | None]
    sector1_ms: Mapped[int | None]
    sector2_ms: Mapped[int | None]
    sector3_ms: Mapped[int | None]
    is_pit_out_lap: Mapped[bool] = mapped_column(server_default=text("false"))


class PitStop(Base):
    __tablename__ = "pit_stops"
    __table_args__ = (UniqueConstraint("session_id", "driver_id", "stop_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"))
    lap_number: Mapped[int]
    stop_number: Mapped[int]
    duration: Mapped[float | None]


class Stint(Base):
    __tablename__ = "stints"
    __table_args__ = (UniqueConstraint("session_id", "driver_id", "stint_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"))
    stint_number: Mapped[int]
    compound: Mapped[str | None] = mapped_column(String(16))
    lap_start: Mapped[int]
    lap_end: Mapped[int]


class Weather(Base):
    __tablename__ = "weather"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    air_temp: Mapped[float | None]
    track_temp: Mapped[float | None]
    humidity: Mapped[float | None]
    pressure: Mapped[float | None]
    rainfall: Mapped[bool | None]
    wind_speed: Mapped[float | None]
    wind_dir: Mapped[int | None]