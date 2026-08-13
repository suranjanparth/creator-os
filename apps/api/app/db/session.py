from sqlalchemy import create_engine
from collections.abc import Generator

from fastapi import HTTPException
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

if settings.database_url is None:
    engine = None
    SessionLocal = None
else:
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db_session() -> Generator[Session, None, None]:
    if SessionLocal is None:
        raise HTTPException(status_code=503, detail="Database is not configured")

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def ensure_local_tables() -> None:
    """Create the persistence schema for the local SQLite development database.

    PostgreSQL deployments keep Alembic migrations as the source of truth, so
    this is intentionally a no-op for any non-SQLite database.
    """
    if SessionLocal is None or engine is None or engine.dialect.name != "sqlite":
        return
    from app.db.base import Base

    Base.metadata.create_all(engine)


def init_database() -> None:
    """Prepare the local SQLite database: create tables and persist the documented development dataset.

    PostgreSQL deployments provision schema via Alembic migrations and seed via
    `python -m app.seed`, so this is a no-op for any non-SQLite database.
    """
    if SessionLocal is None or engine is None or engine.dialect.name != "sqlite":
        return
    ensure_local_tables()
    with SessionLocal() as session:
        from app.domains.content.seed import seed_development_content
        from app.domains.creators.seed import seed_development_creator_profile

        seed_development_creator_profile(session)
        seed_development_content(session)
