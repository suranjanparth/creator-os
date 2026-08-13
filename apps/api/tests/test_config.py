import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_development_settings_default_to_local_sqlite_database() -> None:
    settings = Settings(database_url=None, creator_os_environment="development")

    assert settings.database_url.startswith("sqlite:///")
    assert settings.database_url.endswith("creator_os_local.db")


def test_development_settings_allow_explicit_sqlite_database() -> None:
    settings = Settings(database_url="sqlite:///:memory:", creator_os_environment="development")

    assert settings.database_url == "sqlite:///:memory:"


def test_development_settings_allow_postgresql_database() -> None:
    url = "postgresql+psycopg://creator_os:password@localhost:5432/creator_os"

    settings = Settings(database_url=url, creator_os_environment="development")

    assert settings.database_url == url


def test_development_settings_reject_unsupported_drivers() -> None:
    with pytest.raises(ValidationError, match="PostgreSQL or SQLite driver"):
        Settings(database_url="mysql://creator_os:password@localhost:5432/creator_os", creator_os_environment="development")


def test_non_development_settings_require_database_url() -> None:
    with pytest.raises(ValidationError, match="DATABASE_URL is required outside local development"):
        Settings(database_url=None, creator_os_environment="production")


def test_non_development_settings_reject_sqlite_database() -> None:
    with pytest.raises(ValidationError, match="PostgreSQL driver"):
        Settings(database_url="sqlite:///:memory:", creator_os_environment="production")
