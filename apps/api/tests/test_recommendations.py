from datetime import date

from app.domains.content.ingestion import ingest_content_batch
from app.domains.content.repository import create_content
from app.domains.content.seed import seed_development_content
from app.domains.dashboard.development_data import DEVELOPMENT_CREATOR_ID
from app.domains.recommendations.service import get_recommendations
from app.schemas.content import ContentIngestRequest, CreatorContentCreate


def test_recommendations_return_honest_empty_state(db_session) -> None:
    recommendations = get_recommendations(db_session, "unknown-creator")

    assert recommendations.data_source == "empty"
    assert recommendations.total_posts == 0
    assert recommendations.recommendations == []
    assert recommendations.opportunities == []
    assert recommendations.priority_signal == "Connect your content to unlock recommendations"


def test_recommendations_are_derived_from_persisted_seeded_content(db_session) -> None:
    seed_development_content(db_session)

    recommendations = get_recommendations(db_session, DEVELOPMENT_CREATOR_ID)

    assert recommendations.data_source == "development"
    assert recommendations.total_posts == 6
    assert recommendations.priority_signal == "Carousels are your strongest format"

    first = recommendations.recommendations[0]
    assert first.tag == "Post next"
    assert first.title == "Create a carousel around creative systems topics"
    assert first.sample_size == 2
    assert "9.8% engagement" in first.evidence

    tags = [item.tag for item in recommendations.recommendations]
    assert "Format test" in tags
    assert "Publishing cadence" in tags

    assert any(opportunity.title == "Explore creative systems topics" for opportunity in recommendations.opportunities)


def test_recommendations_return_insufficient_data_honestly(db_session) -> None:
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

    recommendations = get_recommendations(db_session, DEVELOPMENT_CREATOR_ID)

    assert recommendations.data_source == "development"
    assert recommendations.total_posts == 1
    assert recommendations.recommendations == []
    assert recommendations.priority_signal == "Your format mix is still building"


def test_recommendations_endpoint_returns_response_contract(client, db_session) -> None:
    seed_development_content(db_session)

    response = client.get("/api/v1/recommendations", params={"creator_id": DEVELOPMENT_CREATOR_ID})

    assert response.status_code == 200
    payload = response.json()
    assert payload["data_source"] == "development"
    assert payload["total_posts"] == 6
    assert payload["recommendations"][0]["tag"] == "Post next"
    assert payload["recommendations"][0]["sample_size"] == 2
    assert payload["opportunities"][0]["href"] == "/content"


def test_recommendations_endpoint_empty_state_contract(client, db_session) -> None:
    response = client.get("/api/v1/recommendations", params={"creator_id": "no-such-creator"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["data_source"] == "empty"
    assert payload["recommendations"] == []


def test_recommendations_reflect_newly_ingested_content(db_session) -> None:
    from app.schemas.content import ContentIngestItem, ContentIngestRequest

    ingest_content_batch(
        db_session,
        ContentIngestRequest(
            creator_id="creator-new",
            items=[
                ContentIngestItem(
                    id="new-1",
                    platform="LinkedIn",
                    content_type="Text post",
                    category="Solo business",
                    title="A text post",
                    views=2_000,
                    likes=300,
                    comments=80,
                    shares=60,
                    engagement_rate=6.0,
                    published_at=date(2026, 8, 1),
                ),
                ContentIngestItem(
                    id="new-2",
                    platform="LinkedIn",
                    content_type="Text post",
                    category="Solo business",
                    title="Another text post",
                    views=3_000,
                    likes=500,
                    comments=120,
                    shares=100,
                    engagement_rate=7.0,
                    published_at=date(2026, 8, 8),
                ),
            ],
        ),
    )

    recommendations = get_recommendations(db_session, "creator-new")

    assert recommendations.data_source == "development"
    assert recommendations.total_posts == 2
    assert recommendations.recommendations[0].tag == "Post next"
    assert "text post" in recommendations.recommendations[0].title
    assert "solo business" in recommendations.recommendations[0].title
    assert any(item.tag == "Publishing cadence" for item in recommendations.recommendations)
