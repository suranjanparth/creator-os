from datetime import date

from app.domains.content.repository import get_content, list_content
from app.domains.creators.repository import get_creator_profile
from app.domains.ingestion.service import import_creator
from app.schemas.ingestion import CreatorImportRequest, ImportedCreatorProfile


def build_request(creator_id: str = "creator-import", **overrides) -> CreatorImportRequest:
    values = {
        "creator_id": creator_id,
        "profile": ImportedCreatorProfile(
            name="Alex Rivera",
            handle="@alexmakes",
            platform="Instagram",
            niche="Creative systems",
            follower_count=1_200,
        ),
        "content": [
            {
                "id": "ar-1",
                "platform": "Instagram",
                "content_type": "Reel",
                "category": "Creative systems",
                "title": "First reel",
                "views": 5_000,
                "likes": 400,
                "comments": 30,
                "shares": 80,
                "engagement_rate": 8.0,
                "published_at": date(2026, 8, 1),
            },
            {
                "id": "ar-2",
                "platform": "Instagram",
                "content_type": "Carousel",
                "category": "Creative practice",
                "title": "Carousel",
                "views": 2_000,
            },
        ],
    }
    values.update(overrides)
    return CreatorImportRequest(**values)


def test_import_persists_profile_and_content(db_session) -> None:
    response = import_creator(db_session, build_request())

    assert response.profile_status == "created"
    assert response.created == 2
    assert response.updated == 0
    assert response.skipped == 0
    assert response.errors == 0

    profile = get_creator_profile(db_session, "creator-import")
    assert profile is not None
    assert profile.name == "Alex Rivera"
    assert profile.follower_count == 1_200

    stored = list_content(db_session, "creator-import")
    assert [post.id for post in stored] == ["ar-1", "ar-2"]
    assert all(post.creator_id == "creator-import" for post in stored)


def test_import_is_idempotent_across_repeats(db_session) -> None:
    import_creator(db_session, build_request())
    second = import_creator(db_session, build_request())

    assert second.profile_status == "unchanged"
    assert second.created == 0
    assert second.updated == 0
    assert second.skipped == 2
    assert len(list_content(db_session, "creator-import")) == 2


def test_import_updates_changed_content(db_session) -> None:
    import_creator(db_session, build_request())
    changed = build_request(content=[
        {"id": "ar-1", "platform": "Instagram", "content_type": "Reel", "category": "Creative systems", "title": "First reel (updated)", "views": 6_000, "likes": 450, "comments": 40, "shares": 90, "engagement_rate": 8.2, "published_at": date(2026, 8, 1)},
        {"id": "ar-2", "platform": "Instagram", "content_type": "Carousel", "category": "Creative practice", "title": "Carousel", "views": 2_000},
    ])

    response = import_creator(db_session, changed)

    assert response.updated == 1
    assert response.skipped == 1
    updated = get_content(db_session, "ar-1")
    assert updated is not None
    assert updated.title == "First reel (updated)"
    assert updated.views == 6_000


def test_import_updates_changed_profile(db_session) -> None:
    import_creator(db_session, build_request())
    updated_profile = ImportedCreatorProfile(
        name="Alex Rivera",
        handle="@alexmakes",
        platform="Instagram",
        niche="Creative systems & solo business",
        follower_count=2_400,
    )

    response = import_creator(db_session, build_request(profile=updated_profile))

    assert response.profile_status == "updated"
    profile = get_creator_profile(db_session, "creator-import")
    assert profile is not None
    assert profile.niche == "Creative systems & solo business"
    assert profile.follower_count == 2_400


def test_import_keeps_multiple_creators_isolated(db_session) -> None:
    import_creator(db_session, build_request(creator_id="creator-a"))
    import_creator(
        db_session,
        build_request(
            creator_id="creator-b",
            content=[
                {
                    "id": "br-1",
                    "platform": "Instagram",
                    "content_type": "Reel",
                    "category": "Creative systems",
                    "title": "B first reel",
                },
            ],
        ),
    )

    posts_a = list_content(db_session, "creator-a")
    posts_b = list_content(db_session, "creator-b")
    assert {post.creator_id for post in posts_a} == {"creator-a"}
    assert {post.creator_id for post in posts_b} == {"creator-b"}
    assert posts_b[0].id == "br-1"
    assert get_creator_profile(db_session, "creator-b").creator_id == "creator-b"
    assert get_creator_profile(db_session, "creator-a").creator_id == "creator-a"


def test_import_reports_per_item_validation_errors_without_failing_sync(db_session) -> None:
    request = build_request(content=[
        {"id": "ok-1", "platform": "Instagram", "content_type": "Reel", "category": "Creative systems", "title": "Valid post"},
        {"id": "bad-1", "platform": "Instagram"},  # missing content_type/category/title
    ])

    response = import_creator(db_session, request)

    assert response.errors == 1
    assert response.created == 1
    bad = [item for item in response.items if item.id == "bad-1"][0]
    assert bad.status == "error"
    assert "content_type" in bad.detail
    assert get_content(db_session, "bad-1") is None
    assert get_content(db_session, "ok-1") is not None


def test_import_accepts_empty_content_for_profile_only_sync(db_session) -> None:
    response = import_creator(db_session, build_request(content=[]))

    assert response.profile_status == "created"
    assert response.content_received == 0
    assert response.created == 0
    assert get_creator_profile(db_session, "creator-import") is not None
    assert list_content(db_session, "creator-import") == []


def test_import_endpoint_contract(client) -> None:
    payload = {
        "creator_id": "api-import",
        "profile": {"name": "API Creator", "handle": "@apicreator", "platform": "Instagram"},
        "content": [
            {"id": "api-post-1", "platform": "Instagram", "content_type": "Reel", "category": "Creative systems", "title": "API post", "views": 500},
        ],
    }

    response = client.post("/api/v1/ingestion/import", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["creator_id"] == "api-import"
    assert body["profile_status"] == "created"
    assert body["content_received"] == 1
    assert body["created"] == 1
    assert body["updated"] == 0
    assert body["skipped"] == 0
    assert body["errors"] == 0
    assert body["items"] == [{"id": "api-post-1", "status": "created", "detail": None}]


def test_import_endpoint_retrieval_after_ingest(client) -> None:
    payload = {
        "creator_id": "api-import",
        "profile": {"name": "API Creator", "handle": "@apicreator", "platform": "Instagram", "follower_count": 999},
        "content": [{"id": "api-post-1", "platform": "Instagram", "content_type": "Reel", "category": "Creative systems", "title": "API post"}],
    }
    client.post("/api/v1/ingestion/import", json=payload)

    profile = client.get("/api/v1/creators/api-import")
    assert profile.status_code == 200
    assert profile.json()["follower_count"] == 999

    content = client.get("/api/v1/content", params={"creator_id": "api-import"})
    assert content.status_code == 200
    assert len(content.json()) == 1
    assert content.json()[0]["id"] == "api-post-1"


def test_import_endpoint_rejects_request_without_profile(client) -> None:
    response = client.post("/api/v1/ingestion/import", json={"creator_id": "api-import", "content": []})

    assert response.status_code == 422


def test_import_endpoint_rejects_unknown_top_level_fields(client) -> None:
    payload = {
        "creator_id": "api-import",
        "profile": {"name": "API Creator"},
        "content": [],
        "unexpected": True,
    }

    response = client.post("/api/v1/ingestion/import", json=payload)

    assert response.status_code == 422
