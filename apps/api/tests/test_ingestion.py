from datetime import date

from app.domains.content.ingestion import ingest_content_batch
from app.domains.content.intelligence import get_content_intelligence
from app.domains.content.repository import list_content
from app.domains.dashboard.service import get_dashboard
from app.schemas.content import ContentIngestItem, ContentIngestRequest


def build_item(**overrides) -> ContentIngestItem:
    values = {
        "id": "ingested-post",
        "platform": "Instagram",
        "content_type": "Carousel",
        "category": "Creative practice",
        "title": "An ingested post",
        "views": 10_000,
        "likes": 900,
        "comments": 60,
        "shares": 140,
        "engagement_rate": 11.0,
        "published_at": date(2026, 8, 1),
    }
    values.update(overrides)
    return ContentIngestItem(**values)


def test_batch_ingest_creates_all_items(db_session) -> None:
    request = ContentIngestRequest(creator_id="creator-1", items=[build_item(id="post-a"), build_item(id="post-b")])

    response = ingest_content_batch(db_session, request)

    assert response.received == 2
    assert response.created == 2
    assert response.skipped == 0
    assert [item.status for item in response.items] == ["created", "created"]
    assert len(list_content(db_session, "creator-1")) == 2


def test_batch_ingest_skips_existing_and_batch_duplicates(db_session) -> None:
    ingest_content_batch(db_session, ContentIngestRequest(creator_id="creator-1", items=[build_item(id="post-a")]))

    request = ContentIngestRequest(
        creator_id="creator-1",
        items=[build_item(id="post-a"), build_item(id="post-b"), build_item(id="post-b")],
    )

    response = ingest_content_batch(db_session, request)

    assert response.created == 1
    assert response.skipped == 2
    assert [item.status for item in response.items] == ["skipped", "created", "skipped"]
    assert len(list_content(db_session, "creator-1")) == 2


def test_batch_ingest_is_scoped_to_the_request_creator(db_session) -> None:
    ingest_content_batch(
        db_session,
        ContentIngestRequest(creator_id="creator-1", items=[build_item(id="post-a"), build_item(id="post-b")]),
    )

    stored = list_content(db_session, "creator-1")

    assert {post.creator_id for post in stored} == {"creator-1"}
    assert list_content(db_session, "creator-2") == []


def test_ingested_content_reflects_in_dashboard_and_intelligence(db_session) -> None:
    ingest_content_batch(
        db_session,
        ContentIngestRequest(
            creator_id="creator-1",
            items=[
                build_item(id="post-a", views=1_000, likes=100, comments=10, shares=20, engagement_rate=8.0),
                build_item(id="post-b", views=2_000, likes=200, comments=20, shares=40, engagement_rate=9.0),
            ],
        ),
    )

    dashboard = get_dashboard(db_session, "creator-1")

    assert dashboard.metrics[0].value == 3_000
    assert dashboard.metrics[2].value == 2
    assert len(dashboard.performance_trend) == 1

    intelligence = get_content_intelligence(db_session, "creator-1")

    assert len(intelligence.items) == 2
    assert intelligence.items[0].content.id == "post-b"


def test_ingest_endpoint_persists_and_retrieves(client) -> None:
    payload = {
        "creator_id": "creator-api",
        "items": [
            {
                "id": "api-ingest-1",
                "platform": "Instagram",
                "content_type": "Reel",
                "category": "Creative systems",
                "title": "Ingested reel",
                "views": 5_000,
                "likes": 400,
                "comments": 40,
                "shares": 90,
                "engagement_rate": 8.0,
                "published_at": "2026-08-10",
            },
            {
                "id": "api-ingest-2",
                "platform": "LinkedIn",
                "content_type": "Text post",
                "category": "Solo business",
                "title": "Ingested text post",
                "views": 1_200,
                "likes": 100,
                "comments": 20,
                "shares": 10,
            },
        ],
    }

    response = client.post("/api/v1/content/ingest", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["creator_id"] == "creator-api"
    assert body["received"] == 2
    assert body["created"] == 2
    assert body["skipped"] == 0

    listing = client.get("/api/v1/content", params={"creator_id": "creator-api"})

    assert listing.status_code == 200
    assert len(listing.json()) == 2
    assert listing.json()[0]["id"] == "api-ingest-1"


def test_ingest_endpoint_rejects_invalid_payload(client) -> None:
    payload = {"creator_id": "creator-api", "items": [{"id": "", "platform": "Instagram"}]}

    response = client.post("/api/v1/content/ingest", json=payload)

    assert response.status_code == 422


def test_ingest_endpoint_rejects_empty_batch(client) -> None:
    payload = {"creator_id": "creator-api", "items": []}

    response = client.post("/api/v1/content/ingest", json=payload)

    assert response.status_code == 422


def test_ingest_endpoint_rejects_cross_creator_items(client) -> None:
    payload = {
        "creator_id": "creator-1",
        "items": [
            {
                "id": "cross-creator",
                "creator_id": "creator-2",
                "platform": "Instagram",
                "content_type": "Reel",
                "category": "Creative systems",
                "title": "Wrong owner",
            }
        ],
    }

    response = client.post("/api/v1/content/ingest", json=payload)

    assert response.status_code == 422
    assert get_persisted_count(client, "creator-1") == 0
    assert get_persisted_count(client, "creator-2") == 0


def get_persisted_count(client, creator_id: str) -> int:
    listing = client.get("/api/v1/content", params={"creator_id": creator_id})
    return len(listing.json())


def test_ingest_endpoint_skips_duplicates_across_calls(client) -> None:
    payload = {
        "creator_id": "creator-1",
        "items": [
            {
                "id": "stable-post",
                "platform": "Instagram",
                "content_type": "Reel",
                "category": "Creative practice",
                "title": "A stable post",
            }
        ],
    }

    first = client.post("/api/v1/content/ingest", json=payload)
    second = client.post("/api/v1/content/ingest", json=payload)

    assert first.json()["created"] == 1
    assert second.json()["created"] == 0
    assert second.json()["skipped"] == 1
    assert second.json()["items"][0]["detail"] == "already exists"
