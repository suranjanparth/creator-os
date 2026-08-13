from functools import lru_cache
from pathlib import Path

from pydantic import ValidationInfo, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


def _local_sqlite_database_url() -> str:
    """Return a file-backed SQLite URL for local development inside the API directory."""
    db_path = Path(__file__).resolve().parents[2] / "creator_os_local.db"
    return f"sqlite:///{db_path}"


class Settings(BaseSettings):
    """Runtime settings sourced exclusively from environment variables."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    creator_os_environment: str = "development"
    database_url: str | None = None
    cors_origins: str = "http://localhost:3000"
    local_storage_path: Path = Path("storage")

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str | None, info: ValidationInfo) -> str | None:
        if value is None:
            return value

        try:
            url = make_url(value)
        except Exception as error:
            raise ValueError("DATABASE_URL must be a valid SQLAlchemy URL") from error

        environment = info.data.get("creator_os_environment", "development")
        if environment == "development":
            if not (url.drivername.startswith("postgresql") or url.drivername == "sqlite"):
                raise ValueError("DATABASE_URL must use a PostgreSQL or SQLite driver in local development")
        elif not url.drivername.startswith("postgresql"):
            raise ValueError("DATABASE_URL must use a PostgreSQL driver")
        return value

    @model_validator(mode="after")
    def default_local_database(self) -> "Settings":
        if self.database_url is None and self.creator_os_environment == "development":
            self.database_url = _local_sqlite_database_url()
        elif self.database_url is None:
            raise ValueError("DATABASE_URL is required outside local development")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
