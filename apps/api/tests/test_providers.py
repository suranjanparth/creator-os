import pytest

from app.domains.ingestion.providers import (
    ProviderNotConfigured,
    ProviderNotSupported,
    get_provider,
)


def test_get_provider_returns_instagram_adapter_case_insensitively() -> None:
    provider = get_provider("Instagram")

    assert provider.platform == "instagram"
    assert provider.is_configured is False


def test_instagram_provider_raises_without_credentials() -> None:
    provider = get_provider("instagram")

    assert provider.is_configured is False
    with pytest.raises(ProviderNotConfigured, match="INSTAGRAM_ACCESS_TOKEN"):
        provider.fetch_creator()
    with pytest.raises(ProviderNotConfigured, match="INSTAGRAM_ACCESS_TOKEN"):
        provider.fetch_posts()


def test_instagram_provider_never_fabricates_data_when_configured() -> None:
    provider = get_provider("instagram")
    # Simulate a configured connection: it must still refuse to fabricate data.
    provider._access_token = "test-token"
    provider._user_id = "test-user"

    assert provider.is_configured is True
    with pytest.raises(NotImplementedError, match="not implemented"):
        provider.fetch_creator()
    with pytest.raises(NotImplementedError, match="not implemented"):
        provider.fetch_posts()


def test_get_provider_rejects_unsupported_platforms() -> None:
    with pytest.raises(ProviderNotSupported, match="tiktok"):
        get_provider("tiktok")
