from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


class ProviderError(Exception):
    """Base error raised by external-platform provider adapters."""


class ProviderNotConfigured(ProviderError):
    """Raised when a provider requires credentials that are not configured."""


class ProviderNotSupported(ProviderError):
    """Raised when no adapter exists for a requested platform."""


@dataclass(frozen=True)
class ProviderCreator:
    """Authorized creator identity as delivered by an external platform."""

    platform: str
    external_id: str
    display_name: str
    handle: str | None = None
    follower_count: int | None = None
    bio: str | None = None
    profile_url: str | None = None


@dataclass(frozen=True)
class ProviderPost:
    """A published post as delivered by an external platform, before normalization."""

    external_id: str
    media_type: str
    caption: str | None
    published_at: date | None
    views: int | None
    likes: int | None
    comments: int | None
    permalink: str | None = None


class ProviderClient(ABC):
    """Boundary for an authorized external-platform connection.

    Concrete providers own OAuth, token refresh, and platform API calls, and
    return normalized :class:`ProviderCreator` / :class:`ProviderPost` data.
    The ingestion pipeline consumes only normalized payloads, so a provider
    integration can never couple platform specifics into domain logic.
    """

    platform: str

    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """True when credentials are available to reach the platform API."""

    @abstractmethod
    def fetch_creator(self) -> ProviderCreator:
        """Return the authorized creator's identity from the platform."""

    @abstractmethod
    def fetch_posts(self) -> list[ProviderPost]:
        """Return the authorized creator's published posts from the platform."""
