from __future__ import annotations

from datetime import date

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base 


class Season(Base):
    __tablename__ = "seasons"

    year: Mapped[int] = mapped_column(primary_key=True)

    entries: Mapped[list[SeasonEntry]] = relationship(back_populates="season")


class Circuit(Base):
    __tablename__ = "circuits"

    id: Mapped[int] = mapped_column(primary_key=True)
    ergast_ref: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    locality: Mapped[str | None] = mapped_column(String(128))
    country: Mapped[str | None] = mapped_column(String(64))
    lat: Mapped[float | None]
    lng: Mapped[float | None]
    alt: Mapped[int | None]


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(primary_key=True)
    ergast_ref: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    permanent_number: Mapped[int | None]
    code: Mapped[str | None] = mapped_column(String(3))         # VER, LEC, HAM
    forename: Mapped[str] = mapped_column(String(64))
    surname: Mapped[str] = mapped_column(String(64))
    dob: Mapped[date | None]
    nationality: Mapped[str | None] = mapped_column(String(64))

    entries: Mapped[list[SeasonEntry]] = relationship(back_populates="driver")


class Constructor(Base):
    __tablename__ = "constructors"

    id: Mapped[int] = mapped_column(primary_key=True)
    ergast_ref: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    nationality: Mapped[str | None] = mapped_column(String(64))
    color: Mapped[str | None] = mapped_column(String(7))        # hex, e.g. #E8002D
    logo_url: Mapped[str | None] = mapped_column(String(256))

    entries: Mapped[list[SeasonEntry]] = relationship(back_populates="constructor")


class SeasonEntry(Base):
    __tablename__ = "season_entries"
    __table_args__ = (
        # one team per driver per season — the core season_entries invariant
        UniqueConstraint("season_year", "driver_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    season_year: Mapped[int] = mapped_column(ForeignKey("seasons.year"))
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), index=True)
    constructor_id: Mapped[int] = mapped_column(ForeignKey("constructors.id"), index=True)
    driver_number: Mapped[int | None]

    season: Mapped[Season] = relationship(back_populates="entries")
    driver: Mapped[Driver] = relationship(back_populates="entries")
    constructor: Mapped[Constructor] = relationship(back_populates="entries")