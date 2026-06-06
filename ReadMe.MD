# F1 Analysis & Prediction Platform

Historical Formula 1 analysis and race-result prediction. React + TypeScript
frontend, FastAPI + PostgreSQL backend, and ML models that predict finishing
order. Portfolio project.

Full schema, ERD, and rationale: [`docs/F1_database_design_v2.pdf`](docs/F1_database_design_v2.pdf).

## Database

PostgreSQL, normalized (3NF) with JSONB where a document fits better. It bridges
two sources — Jolpica/Ergast (results & qualifying, 1950+) and OpenF1 (telemetry
& live timing, 2023+) — mirrored into our own DB rather than queried live, since
the free APIs are deprecated / rate-limited.

```mermaid
erDiagram
    SEASONS      ||--o{ RACES          : has
    SEASONS      ||--o{ SEASON_ENTRIES : lists
    CIRCUITS     ||--o{ RACES          : hosts
    DRIVERS      ||--o{ SEASON_ENTRIES : enters
    CONSTRUCTORS ||--o{ SEASON_ENTRIES : fields
    RACES        ||--o{ SESSIONS       : has
    SESSIONS     ||--o{ RESULTS        : produces
    SESSIONS     ||--o{ QUALIFYING     : produces
    SESSIONS     ||--o{ LAPS           : records
    SESSIONS     ||--o{ PIT_STOPS      : records
    SESSIONS     ||--o{ STINTS         : records
    SESSIONS     ||--o{ WEATHER        : records
    SESSIONS     ||--o{ LIVE_TIMING    : streams
    SESSIONS     ||--o{ PREDICTIONS    : generates
    DRIVERS      ||--o{ RESULTS        : in
    DRIVERS      ||--o{ QUALIFYING     : in
    DRIVERS      ||--o{ LAPS           : in
    DRIVERS      ||--o{ PIT_STOPS      : in
    DRIVERS      ||--o{ STINTS         : in
    DRIVERS      ||--o{ LIVE_TIMING    : in
    CONSTRUCTORS ||--o{ RESULTS        : in
    CONSTRUCTORS ||--o{ QUALIFYING     : in
    STATUSES     ||--o{ RESULTS        : classifies

    SEASONS {
        int year PK
    }
    CIRCUITS {
        int id PK
        string ergast_ref
        string name
    }
    DRIVERS {
        int id PK
        string code
        string surname
    }
    CONSTRUCTORS {
        int id PK
        string name
        string color
    }
    SEASON_ENTRIES {
        int id PK
        int season_year FK
        int driver_id FK
        int constructor_id FK
        int driver_number
    }
    RACES {
        int id PK
        int season_year FK
        int circuit_id FK
        int round
    }
    SESSIONS {
        int id PK
        int race_id FK
        string type
        int openf1_session_key
    }
    STATUSES {
        int id PK
        string label
    }
    RESULTS {
        int id PK
        int session_id FK
        int driver_id FK
        int constructor_id FK
        int status_id FK
        int position
    }
    QUALIFYING {
        int id PK
        int session_id FK
        int driver_id FK
        int constructor_id FK
        int position
    }
    LAPS {
        int id PK
        int session_id FK
        int driver_id FK
        int lap_number
    }
    PIT_STOPS {
        int id PK
        int session_id FK
        int driver_id FK
        int lap_number
    }
    STINTS {
        int id PK
        int session_id FK
        int driver_id FK
        string compound
    }
    WEATHER {
        int id PK
        int session_id FK
        timestamp recorded_at
    }
    LIVE_TIMING {
        int id PK
        int session_id FK
        int driver_id FK
        int lap_number
        int position
    }
    PREDICTIONS {
        int id PK
        int session_id FK
        int lap_checkpoint
        json payload
    }
```

### Why PostgreSQL, not MongoDB

- The workload is relational and analytical — cross-season joins, aggregations,
  and foreign-key integrity across drivers, constructors, and sessions. SQL fits
  it directly; Mongo's `$lookup` is awkward for multi-way joins.
- The only places that want a flexible document — `predictions.payload` and the
  live race snapshot — are covered by Postgres JSONB. So we get document
  flexibility without a second datastore, on one Neon free-tier bill.

### `live_timing` is transient

- One row per driver per lap = the full running order at the end of each lap,
  streamed from OpenF1 during a race.
- The model reads the trailing ~10 laps at each checkpoint; rows for a session
  are deleted once its official `results` are ingested. It never feeds `results`
  (which is set only by the final classification).

## Stack

| Layer    | Choice                                       |
|----------|----------------------------------------------|
| Frontend | React + TypeScript (Vite), React Query, Recharts, Tailwind |
| Backend  | FastAPI, SQLAlchemy 2.0, Alembic (Python 3.13) |
| Database | PostgreSQL (local via Docker; Neon in prod)  |
| ML       | scikit-learn / LightGBM (trained offline)    |
| Hosting  | Cloudflare Pages + Render + Neon ($0/month)  |

## Run locally

```bash
docker compose up --build        # API on :8000, Postgres on :5432

cd backend
alembic upgrade head             # apply migrations
uvicorn app.main:app --reload

cd frontend && npm install && npm run dev   # http://localhost:5173
```