from datetime import date

import pytest

from app.domains.content.repository import create_content
from app.domains.content.seed import seed_development_content
from app.domains.creators.repository import create_creator_profile, get_creator_profile
from app.domains.creators.seed import seed_development_creator_profile
from app.domains.creators.service import save_creator_profile
from app.domains.dashboard.development_data import DEVELOPMENT_CREATOR_ID
from app.domains.dashboard.service import get_dashboard
from app.schemas.content import CreatorContentCreate
from app.schemas.creator import CreatorProfileCreate


def build_profile(**overrides) -> CreatorProfileCreate:
    values = {
        "creator_id": "creator-1",
        "name": "Jordan Lee",
        "handle": "@jordanmakes",
        "niche": "Creative systems",
        "platform": "Instagram",
        "audience": "Ambitious creatives",
        "follower_count": 12_500,
    }
    values.update(overrides)
    return CreatorProfileCreate(**values)


def build_content(**overrides) -> CreatorContentCreate:
    values = {
        "id": "profile-post",
        "creator_id": "creator-1",
        "platform": "Instagram",
        "content_type": "Reel",
        "category": "Creative systems",
        "title": "A profile-scoped post",
        "views": 10_000,
        "likes": 900,
        "comments": 60,
        "shares": 140,
        "engagement_rate": 11.0,
        "published_at": date(2026, 8, 1),
    }
    values.update(overrides)
    return CreatorContentCreate(**values)


def test_creator_profile_persists_and_retrieves(db_session) -> None:
    response = save_creator_profile(db_session, build_profile())

    assert response.creator_id == "creator-1"
    assert response.name == "Jordan Lee"
    assert response.follower_count == 12_500
    assert response.created_at is not None
    assert response.updated_at is not None

    record = get_creator_profile(db_session, "creator-1")

    assert record is not None
    assert record.name == "Jordan Lee"
    assert record.handle == "@jordanmakes"


def test_creator_profile_retrieval_is_scoped_to_creator(db_session) -> None:
    create_creator_profile(db_session, build_profile(creator_id="creator-a"))
    create_creator_profile(db_session, build_profile(creator_id="creator-b", name="Another Creator"))

    assert get_creator_profile(db_session, "creator-a").name == "Jordan Lee"
    assert get_creator_profile(db_session, "creator-b").name == "Another Creator"
    assert get_creator_profile(db_session, "creator-c") is None


def test_missing_creator_profile_returns_none(db_session) -> None:
    assert get_creator_profile(db_session, "no-such-creator") is None


def test_duplicate_creator_profile_is_rejected(db_session) -> None:
    save_creator_profile(db_session, build_profile())

    with pytest.raises(ValueError, match="already exists"):
        save_creator_profile(db_session, build_profile())


def test_seed_development_creator_profile_is_idempotent(db_session) -> None:
    assert seed_development_creator_profile(db_session) == 1
    assert seed_development_creator_profile(db_session) == 0

    record = get_creator_profile(db_session, DEVELOPMENT_CREATOR_ID)

    assert record is not None
    assert record.name == "Maya Chen"
    assert record.follower_count == 84_200


def test_creator_profile_endpoint_creates_and_retrieves(client) -> None:
    payload = {
        "creator_id": "api-creator",
        "name": "Sam Patel",
        "handle": "@samsystem",
        "niche": "Solo business",
        "platform": "LinkedIn",
        "audience": "Solo founders",
        "follower_count": 4_000,
    }

    create_response = client.post("/api/v1/creators", json=payload)

    assert create_response.status_code == 201
    assert create_response.json()["creator_id"] == "api-creator"
    assert create_response.json()["name"] == "Sam Patel"

    retrieve_response = client.get("/api/v1/creators/api-creator")

    assert retrieve_response.status_code == 200
    body = retrieve_response.json()
    assert body["handle"] == "@samsystem"
    assert body["niche"] == "Solo business"
    assert body["platform"] == "LinkedIn"
    assert body["follower_count"] == 4_000
    assert "created_at" in body
    assert "updated_at" in body


def test_creator_profile_endpoint_returns_404_for_missing_creator(client) -> None:
    response = client.get("/api/v1/creators/unknown")

    assert response.status_code == 404


def test_creator_profiles_endpoint_lists_persisted_creators_by_name(client, db_session) -> None:
    create_creator_profile(db_session, build_profile(creator_id="zara", name="Zara Ali"))
    create_creator_profile(db_session, build_profile(creator_id="alex", name="Alex Rivera"))

    response = client.get("/api/v1/creators")

    assert response.status_code == 200
    assert [profile["creator_id"] for profile in response.json()] == ["alex", "zara"]


def test_creator_profile_endpoint_rejects_duplicates(client) -> None:
    payload = build_profile().model_dump()

    assert client.post("/api/v1/creators", json=payload).status_code == 201
    response = client.post("/api/v1/creators", json=payload)

    assert response.status_code == 409


def test_dashboard_uses_persisted_creator_profile(client, db_session) -> None:
    create_creator_profile(db_session, build_profile(creator_id="creator-1", follower_count=25_000))
    create_content(db_session, build_content())

    dashboard = get_dashboard(db_session, "creator-1")

    assert dashboard.data_source == "development"
    assert dashboard.creator is not None
    assert dashboard.creator.name == "Jordan Lee"
    assert dashboard.creator.followers == 25_000


def test_dashboard_endpoint_uses_persisted_creator_profile(client, db_session) -> None:
    create_creator_profile(db_session, build_profile(creator_id="creator-1", follower_count=25_000))
    create_content(db_session, build_content())

    response = client.get("/api/v1/dashboard", params={"creator_id": "creator-1"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["creator"] == {
        "name": "Jordan Lee",
        "handle": "@jordanmakes",
        "niche": "Creative systems",
        "audience": "Ambitious creatives",
        "followers": 25_000,
    }


def test_dashboard_empty_state_still_shows_persisted_creator(client, db_session) -> None:
    create_creator_profile(db_session, build_profile(creator_id="creator-1"))

    response = client.get("/api/v1/dashboard", params={"creator_id": "creator-1"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["data_source"] == "empty"
    assert payload["creator"]["name"] == "Jordan Lee"
    assert payload["metrics"] == []


def test_seeded_posts_support_dashboard_with_persisted_profile(db_session) -> None:
    seed_development_creator_profile(db_session)
    seed_development_content(db_session)

    dashboard = get_dashboard(db_session, DEVELOPMENT_CREATOR_ID)

    assert dashboard.creator is not None
    assert dashboard.creator.handle == "@mayamakes"
    assert dashboard.metrics[0].value == 398_400
