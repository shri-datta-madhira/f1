from __future__ import annotations

from datetime import date, datetime, time
from typing import TYPE_CHECKING
from enum import StrEnum
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from app.database import Base

if TYPE_CHECKING:
    from app.models.reference import Circuit, Constructor, Driver, Season


class GrandPrix(Base):
    __tablename__ = "grand_prix"
    __table_args__ = (UniqueConstraint("season_year", "round"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    season_year: Mapped[int] = mapped_column(ForeignKey("seasons.year"))  # uq leftmost covers it
    round: Mapped[int]
    circuit_id: Mapped[int] = mapped_column(ForeignKey("circuits.id"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    race_date: Mapped[date]
    race_time: Mapped[time | None]

    sessions: Mapped[list[Session]] = relationship(back_populates="grand_prix")
    season: Mapped[Season] = relationship()
    circuit: Mapped[Circuit] = relationship()

class SessionType(StrEnum):
    FP1 = "fp1"
    FP2 = "fp2"
    FP3 = "fp3"
    SPRINT_QUALIFYING = "sprint_qualifying"  # "Sprint Shootout" in 2023
    QUALIFYING = "qualifying"
    SPRINT = "sprint"
    RACE = "race"

class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        # one session of each type per weekend (one race, one sprint, one qualifying, ...)
        UniqueConstraint("grand_prix_id", "type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    grand_prix_id: Mapped[int] = mapped_column(ForeignKey("grand_prix.id"), index=True)
    type: Mapped[SessionType] = mapped_column(
        SQLEnum(
            SessionType,
            name="session_type",
            native_enum=False,      # store as VARCHAR + CHECK, not a native PG enum
            create_constraint=True, # without this, no CHECK is emitted
            length=24,
            values_callable=lambda e: [m.value for m in e],  # store "race", not "RACE"
        )
    )  
    scheduled_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    openf1_session_key: Mapped[int | None] = mapped_column(unique=True)

    grand_prix: Mapped[GrandPrix] = relationship(back_populates="sessions")
    results: Mapped[list[RaceResults]] = relationship(back_populates="session")
    qualifying: Mapped[list[QualiResults]] = relationship(back_populates="session")


class Status(Base):
    __tablename__ = "statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(64), unique=True)


class RaceResults(Base):
    """Official classification of any racing session: grand prix race AND sprint."""
    __tablename__ = "race_results"
    __table_args__ = (UniqueConstraint("session_id", "driver_id"),)  # uq leftmost covers session_id

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), index=True)
    constructor_id: Mapped[int] = mapped_column(ForeignKey("constructors.id"), index=True)
    status_id: Mapped[int] = mapped_column(ForeignKey("statuses.id"))  # low-cardinality, not indexed
    grid: Mapped[int | None]
    position: Mapped[int | None]
    points: Mapped[float] = mapped_column(server_default=text("0"))
    laps_completed: Mapped[int | None]
    fastest_lap_rank: Mapped[int | None]

    session: Mapped[Session] = relationship(back_populates="results")
    driver: Mapped[Driver] = relationship()
    constructor: Mapped[Constructor] = relationship()
    status: Mapped[Status] = relationship()


class QualiResults(Base):
    """Official classification of any qualifying session: grand prix qualifying AND sprint."""
    __tablename__ = "quali_results"
    __table_args__ = (UniqueConstraint("session_id", "driver_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), index=True)
    constructor_id: Mapped[int] = mapped_column(ForeignKey("constructors.id"))
    position: Mapped[int | None]
    q1: Mapped[str | None] = mapped_column(String(16))
    q2: Mapped[str | None] = mapped_column(String(16))
    q3: Mapped[str | None] = mapped_column(String(16))

    session: Mapped[Session] = relationship(back_populates="qualifying")
    driver: Mapped[Driver] = relationship()