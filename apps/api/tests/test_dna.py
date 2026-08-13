from datetime import date

from app.domains.content.repository import create_content
from app.domains.content.seed import seed_development_content
from app.domains.creators.seed import seed_development_creator_profile
from app.domains.dashboard.development_data import DEVELOPMENT_CREATOR_ID
from app.domains.dna.service import get_creator_dna
from app.schemas.content import CreatorContentCreate


def test_dna_returns_honest_empty_state(db_session) -> None:
    dna = get_creator_dna(db_session, "unknown-creator")

    assert dna.data_source == "empty"
    assert dna.total_posts == 0
    assert dna.identity is None
    assert dna.platforms == []
    assert dna.formats == []
    assert dna.insights[0].title == "No published content yet"


def test_dna_is_derived_from_persisted_seeded_content(db_session) -> None:
    seed_development_creator_profile(db_session)
    seed_development_content(db_session)

    dna = get_creator_dna(db_session, DEVELOPMENT_CREATOR_ID)

    assert dna.data_source == "development"
    assert dna.total_posts == 6
    assert dna.identity is not None
    assert dna.identity.name == "Maya Chen"
    assert dna.identity.audience == "Ambitious creatives, 24-34"
    assert dna.platforms[0].name == "Instagram"
    assert dna.platforms[0].count == 3
    assert dna.platforms[0].share == 50.0
    assert dna.best_format is not None
    assert dna.best_format.name == "Carousel"
    assert dna.best_format.average_engagement_rate == 9.8
    assert dna.best_format.sample_size == 2
    assert dna.engagement_benchmark is not None
    assert dna.engagement_benchmark.sample_size == 6
    titles = {insight.title for insight in dna.insights}
    assert "Instagram is your primary platform" in titles
    assert "Carousels lead your engagement" in titles
    assert "You publish about every 3 days" in titles


def test_dna_returns_insufficient_data_honestly(db_session) -> None:
    create_content(
        db_session,
        CreatorContentCreate(
            id="only-post",
            creator_id=DEVELOPMENT_CREATOR_ID,
            platform="Instagram",
            content_type="Reel",
            category="Creative systems",
            title="A single post",
            views=10_000,
            likes=100,
            comments=5,
            shares=20,
            engagement_rate=1.3,
        ),
    )

    dna = get_creator_dna(db_session, DEVELOPMENT_CREATOR_ID)

    assert dna.data_source == "development"
    assert dna.total_posts == 1
    assert dna.best_format is None
    assert any(insight.title == "Format comparison needs more data" for insight in dna.insights)


def test_dna_endpoint_returns_response_contract(client, db_session) -> None:
    seed_development_creator_profile(db_session)
    seed_development_content(db_session)

    response = client.get("/api/v1/creator-dna")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data_source"] == "development"
    assert payload["total_posts"] == 6
    assert payload["identity"]["name"] == "Maya Chen"
    assert payload["platforms"][0] == {"name": "Instagram", "count": 3, "share": 50.0}
    assert payload["best_format"]["name"] == "Carousel"
    assert payload["insights"][0]["title"] == "Instagram is your primary platform"


def test_dna_endpoint_empty_state_contract(client, db_session) -> None:
    response = client.get("/api/v1/creator-dna", params={"creator_id": "no-such-creator"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["data_source"] == "empty"
    assert payload["total_posts"] == 0
    assert payload["insights"][0]["title"] == "No published content yet"


def test_dna_reflects_newly_ingested_content(db_session) -> None:
    from app.domains.content.ingestion import ingest_content_batch
    from app.schemas.content import ContentIngestItem, ContentIngestRequest

    ingest_content_batch(
        db_session,
        ContentIngestRequest(
            creator_id="creator-new",
            items=[
                ContentIngestItem(
                    id="new-1",
                    platform="TikTok",
                    content_type="Video",
                    category="Creative systems",
                    title="A video post",
                    views=5_000,
                    likes=500,
                    comments=60,
                    shares=100,
                    engagement_rate=12.0,
                    published_at=date(2026, 8, 1),
                ),
                ContentIngestItem(
                    id="new-2",
                    platform="TikTok",
                    content_type="Video",
                    category="Creative systems",
                    title="Another video post",
                    views=4_000,
                    likes=400,
                    comments=40,
                    shares=80,
                    engagement_rate=11.0,
                    published_at=date(2026, 8, 5),
                ),
            ],
        ),
    )

    dna = get_creator_dna(db_session, "creator-new")

    assert dna.total_posts == 2
    assert dna.platforms[0].name == "TikTok"
    assert dna.best_format is not None
    assert dna.best_format.name == "Video"
    assert dna.best_format.average_engagement_rate == 11.5
    assert any("every 4 days" in insight.title for insight in dna.insights)
