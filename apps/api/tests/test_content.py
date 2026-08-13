from datetime import date

import pytest

from app.domains.content.repository import list_content
from app.domains.content.seed import seed_development_content
from app.domains.content.service import get_creator_content, ingest_content
from app.domains.dashboard.development_data import DEVELOPMENT_CREATOR_ID
from app.schemas.content import CreatorContentCreate


def build_content(**overrides) -> CreatorContentCreate:
    values = {
        "id": "post-1",
        "creator_id": "creator-1",
        "platform": "Instagram",
        "content_type": "Reel",
        "category": "Creative systems",
        "title": "A post",
        "views": 1_000,
        "likes": 100,
        "comments": 10,
        "shares": 20,
        "engagement_rate": 1.0,
        "published_at": date(2026, 8, 1),
    }
    values.update(overrides)
    return CreatorContentCreate(**values)


def test_content_insertion_and_retrieval(db_session) -> None:
    created = ingest_content(db_session, build_content())

    assert created.id == "post-1"

    records = get_creator_content(db_session, "creator-1")

    assert len(records) == 1
    assert records[0].title == "A post"


def test_content_retrieval_is_scoped_to_creator(db_session) -> None:
    ingest_content(db_session, build_content(id="post-1", creator_id="creator-1"))
    ingest_content(db_session, build_content(id="post-2", creator_id="creator-2"))

    creator_one = list_content(db_session, "creator-1")
    creator_two = list_content(db_session, "creator-2")

    assert [record.id for record in creator_one] == ["post-1"]
    assert [record.id for record in creator_two] == ["post-2"]


def test_duplicate_content_is_rejected(db_session) -> None:
    ingest_content(db_session, build_content())

    with pytest.raises(ValueError, match="already exists"):
        ingest_content(db_session, build_content())


def test_seed_development_content_is_idempotent(db_session) -> None:
    assert seed_development_content(db_session) == 6
    assert seed_development_content(db_session) == 0
    assert len(list_content(db_session, DEVELOPMENT_CREATOR_ID)) == 6


def test_content_endpoint_inserts_and_lists(client) -> None:
    payload = {
        "id": "api-post-1",
        "creator_id": "creator-api",
        "platform": "TikTok",
        "content_type": "Video",
        "category": "Creative systems",
        "title": "A persisted post",
        "views": 5_000,
        "likes": 400,
        "comments": 40,
        "shares": 90,
        "engagement_rate": 8.0,
        "published_at": "2026-08-10",
    }

    create_response = client.post("/api/v1/content", json=payload)

    assert create_response.status_code == 201
    assert create_response.json()["id"] == "api-post-1"

    list_response = client.get("/api/v1/content", params={"creator_id": "creator-api"})

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["title"] == "A persisted post"


def test_content_endpoint_scopes_listing_to_creator(client) -> None:
    for index in range(2):
        client.post(
            "/api/v1/content",
            json={
                "id": f"scoped-{index}",
                "creator_id": f"creator-{index}",
                "platform": "Instagram",
                "content_type": "Reel",
                "category": "Creative practice",
                "title": f"Post {index}",
            },
        )

    response = client.get("/api/v1/content", params={"creator_id": "creator-0"})

    assert [item["id"] for item in response.json()] == ["scoped-0"]


def test_content_endpoint_rejects_duplicates(client) -> None:
    payload = {
        "id": "duplicate-post",
        "creator_id": "creator-1",
        "platform": "Instagram",
        "content_type": "Reel",
        "category": "Creative systems",
        "title": "Duplicate",
    }

    assert client.post("/api/v1/content", json=payload).status_code == 201
    response = client.post("/api/v1/content", json=payload)

    assert response.status_code == 409
