from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app.db import session as session_module
from app.db.models.content import CreatorContent
from app.db.models.creator_profile import CreatorProfile


def test_init_database_provisions_local_sqlite_database(tmp_path, monkeypatch) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'local.db'}")
    monkeypatch.setattr(session_module, "engine", engine)
    monkeypatch.setattr(session_module, "SessionLocal", sessionmaker(bind=engine, autoflush=False, autocommit=False))

    session_module.init_database()

    with session_module.SessionLocal() as testing_session:
        content_count = testing_session.scalar(select(func.count()).select_from(CreatorContent))
        profile_count = testing_session.scalar(select(func.count()).select_from(CreatorProfile))
    assert content_count == 6
    assert profile_count == 1


def test_init_database_is_idempotent(tmp_path, monkeypatch) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'local.db'}")
    monkeypatch.setattr(session_module, "engine", engine)
    monkeypatch.setattr(session_module, "SessionLocal", sessionmaker(bind=engine, autoflush=False, autocommit=False))

    session_module.init_database()
    session_module.init_database()

    with session_module.SessionLocal() as testing_session:
        content_count = testing_session.scalar(select(func.count()).select_from(CreatorContent))
    assert content_count == 6


def test_init_database_is_a_noop_for_non_sqlite_databases(monkeypatch) -> None:
    engine = create_engine("postgresql+psycopg://creator_os:password@localhost:5432/creator_os")
    monkeypatch.setattr(session_module, "engine", engine)
    monkeypatch.setattr(session_module, "SessionLocal", sessionmaker(bind=engine, autoflush=False, autocommit=False))

    session_module.init_database()
