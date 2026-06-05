from sqlalchemy import create_engine, text

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)


def check_connection() -> None:
    """Run a trivial query to confirm the database is reachable."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))