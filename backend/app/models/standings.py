"""Championship standings snapshots, one set per grand prix weekend.

Why these are fetched from Jolpica and stored — not computed from results:
F1 standings are NOT a naive SUM(points) over race_results. Dropped-score
rules applied until 1990 (only a driver's best N results counted), points
systems changed repeatedly, shared drives in the 1950s split points
fractionally, and drivers have been excluded from a championship while
their race results stand (Schumacher, 1997). Jolpica serves the official
standings after every round; we snapshot them per grand prix and treat
that as the source of truth.

Grain: one row per (grand_prix, driver) and one per (grand_prix,
constructor), representing the championship state AFTER that weekend
concludes (race + sprint points included).

Expected gaps the ingester must treat as valid, not as errors:
- Constructor standings do not exist before 1958 (no constructors'
  championship until then).
- A driver excluded from the championship has position_text "D"/"E"
  and no numeric position.
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.event import GrandPrix
from app.models.reference import Constructor, Driver


class DriverStanding(Base):
    """Drivers' championship state after one grand prix weekend.

    No constructor_id here on purpose: Jolpica attaches a constructor
    list to each driver standing, but driver->team association already
    has two authoritative homes (season_entries for the season roster,
    race_results.constructor_id for per-session truth). Duplicating it
    a third time invites drift.
    """

    __tablename__ = "driver_standings"
    __table_args__ = (
        # Doubles as the read index for the race page:
        # WHERE grand_prix_id = :id uses the leftmost column.
        UniqueConstraint("grand_prix_id", "driver_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    grand_prix_id: Mapped[int] = mapped_column(ForeignKey("grand_prix.id"))
    driver_id: Mapped[int] = mapped_column(
        ForeignKey("drivers.id"),
        index=True,  # season-arc queries: one driver across many rounds
    )

    # Nullable: excluded/disqualified drivers carry no numeric position.
    position: Mapped[int | None]
    # Raw Jolpica positionText ("1", "D", "E") kept for fidelity;
    # position is the sortable projection of it.
    position_text: Mapped[str] = mapped_column(String(4))
    # Numeric, not Float: fractional points are exact values
    # (shared drives split points; half-points races award e.g. 12.5).
    points: Mapped[Decimal] = mapped_column(Numeric(6, 2))
    # Race wins accumulated in the season so far (the championship
    # tiebreaker), as reported by Jolpica.
    wins: Mapped[int]

    # One-directional on purpose: adding back_populates would mean
    # editing event.py/reference.py outside this change's scope.
    grand_prix: Mapped[GrandPrix] = relationship()
    driver: Mapped[Driver] = relationship()


class ConstructorStanding(Base):
    """Constructors' championship state after one grand prix weekend."""

    __tablename__ = "constructor_standings"
    __table_args__ = (UniqueConstraint("grand_prix_id", "constructor_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    grand_prix_id: Mapped[int] = mapped_column(ForeignKey("grand_prix.id"))
    constructor_id: Mapped[int] = mapped_column(
        ForeignKey("constructors.id"),
        index=True,
    )

    position: Mapped[int | None]
    position_text: Mapped[str] = mapped_column(String(4))
    points: Mapped[Decimal] = mapped_column(Numeric(7, 2))
    wins: Mapped[int]

    grand_prix: Mapped[GrandPrix] = relationship()
    constructor: Mapped[Constructor] = relationship()