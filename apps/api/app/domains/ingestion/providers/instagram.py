import os

from app.domains.ingestion.providers.base import (
    ProviderClient,
    ProviderCreator,
    ProviderNotConfigured,
    ProviderNotSupported,
    ProviderPost,
)

# Credentials a real Meta/Instagram Graph API integration will require.
# These are read from the environment; they are never committed or exposed.
REQUIRED_ENVIRONMENT_VARIABLES = (
    "INSTAGRAM_APP_ID",
    "INSTAGRAM_APP_SECRET",
    "INSTAGRAM_REDIRECT_URI",
    "INSTAGRAM_ACCESS_TOKEN",
    "INSTAGRAM_USER_ID",
)


class InstagramProvider(ProviderClient):
    """Adapter for an authorized Instagram (Meta Graph API) connection.

    This is the integration seam for the future Instagram flow. It never
    fabricates platform data: until a live Meta API integration is implemented,
    fetching creator identity or posts raises :class:`ProviderNotConfigured`
    (when credentials are missing) or :class:`NotImplementedError` (when the
    live API call is not yet implemented).
    """

    platform = "instagram"

    def __init__(self, access_token: str | None = None, user_id: str | None = None) -> None:
        self._access_token = access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self._user_id = user_id or os.getenv("INSTAGRAM_USER_ID")

    @property
    def is_configured(self) -> bool:
        return bool(self._access_token and self._user_id)

    def _require_credentials(self) -> None:
        if not self.is_configured:
            raise ProviderNotConfigured(
                "Instagram provider requires INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_USER_ID "
                "from an authorized Meta Graph API app. No credentials are configured."
            )

    def fetch_creator(self) -> ProviderCreator:
        self._require_credentials()
        raise NotImplementedError(
            "The live Instagram Graph API integration is not implemented yet; no creator data is fabricated."
        )

    def fetch_posts(self) -> list[ProviderPost]:
        self._require_credentials()
        raise NotImplementedError(
            "The live Instagram Graph API integration is not implemented yet; no post data is fabricated."
        )


def get_provider(platform: str) -> ProviderClient:
    """Return the configured provider adapter for a platform, if supported."""
    normalized = platform.strip().lower()
    if normalized == "instagram":
        return InstagramProvider()
    raise ProviderNotSupported(f"No provider adapter exists for platform '{platform}'")
