from datetime import date

from app.domains.content.repository import create_content
from app.domains.content.seed import seed_development_content
from app.domains.creators.seed import seed_development_creator_profile
from app.domains.dashboard.development_data import DEVELOPMENT_CREATOR_ID
from app.domains.dashboard.service import get_dashboard, get_empty_dashboard
from app.schemas.content import CreatorContentCreate


def build_content(**overrides) -> CreatorContentCreate:
    values = {
        "id": "dashboard-post",
        "creator_id": DEVELOPMENT_CREATOR_ID,
        "platform": "Instagram",
        "content_type": "Carousel",
        "category": "Creative practice",
        "title": "A dashboard post",
        "views": 10_000,
        "likes": 900,
        "comments": 60,
        "shares": 140,
        "engagement_rate": 11.0,
        "published_at": date(2026, 8, 1),
    }
    values.update(overrides)
    return CreatorContentCreate(**values)


def test_dashboard_derives_metrics_from_persisted_seeded_data(db_session) -> None:
    seed_development_creator_profile(db_session)
    seed_development_content(db_session)

    dashboard = get_dashboard(db_session, DEVELOPMENT_CREATOR_ID)

    assert dashboard.data_source == "development"
    assert dashboard.creator is not None
    assert dashboard.creator.name == "Maya Chen"
    assert [metric.model_dump() for metric in dashboard.metrics] == [
        {"label": "Total views", "value": 398_400, "change": None, "detail": None},
        {"label": "Engagement rate", "value": 9.2, "change": None, "detail": None},
        {"label": "Total content", "value": 6, "change": None, "detail": None},
    ]
    assert len(dashboard.performance_trend) == 6
    assert dashboard.performance_trend[0].date == date(2026, 7, 27)
    assert dashboard.performance_trend[0].views == 52_200
    assert dashboard.performance_trend[-1].date == date(2026, 8, 9)
    assert dashboard.performance_trend[-1].views == 124_000
    assert dashboard.recent_content[0].published_at == date(2026, 8, 9)
    assert dashboard.best_performing_content[0].content_type == "Carousel"
    assert dashboard.insight.model_dump() == {
        "title": "Carousels lead engagement",
        "summary": "Carousel posts average 9.8% engagement across 2 posts, making them the strongest format to build on next.",
        "evidence": "Based on 2 carousel posts across 6 posts.",
        "confidence": 0.33,
        "method": "Initial intelligence layer: deterministic format-performance rule.",
    }


def test_dashboard_derives_correct_metrics_from_custom_persisted_posts(db_session) -> None:
    create_content(db_session, build_content(id="post-1", views=30_000, likes=3_000, comments=300, shares=600, engagement_rate=13.0))
    create_content(db_session, build_content(id="post-2", views=10_000, likes=500, comments=100, shares=100, engagement_rate=7.0))

    dashboard = get_dashboard(db_session, DEVELOPMENT_CREATOR_ID)

    assert [metric.model_dump() for metric in dashboard.metrics] == [
        {"label": "Total views", "value": 40_000, "change": None, "detail": None},
        {"label": "Engagement rate", "value": 11.5, "change": None, "detail": None},
        {"label": "Total content", "value": 2, "change": None, "detail": None},
    ]
    assert [point.date for point in dashboard.performance_trend] == [date(2026, 8, 1)]
    assert dashboard.best_performing_content[0].id == "post-1"


def test_dashboard_retrieval_is_scoped_to_creator(db_session) -> None:
    create_content(db_session, build_content(id="post-a", creator_id="creator-a"))
    create_content(db_session, build_content(id="post-b", creator_id="creator-b"))

    dashboard_a = get_dashboard(db_session, "creator-a")

    assert dashboard_a.metrics[2].value == 1
    assert dashboard_a.recent_content[0].id == "post-a"


def test_dashboard_returns_honest_empty_state_when_no_posts(db_session) -> None:
    dashboard = get_dashboard(db_session, "unknown-creator")

    assert dashboard.data_source == "empty"
    assert dashboard.creator is None
    assert dashboard.metrics == []
    assert dashboard.performance_trend == []
    assert dashboard.recent_content == []
    assert dashboard.insight.title == "Connect your creator data to unlock insights"


def test_dashboard_insufficient_data_returns_honest_insight(db_session) -> None:
    create_content(db_session, build_content())

    dashboard = get_dashboard(db_session, DEVELOPMENT_CREATOR_ID)

    assert dashboard.data_source == "development"
    assert dashboard.metrics[2].value == 1
    assert len(dashboard.performance_trend) == 1
    assert dashboard.insight.title == "Not enough format data yet"
    assert dashboard.insight.confidence is None
    assert dashboard.insight.evidence is None


def test_dashboard_endpoint_returns_response_contract(client, db_session) -> None:
    seed_development_creator_profile(db_session)
    seed_development_content(db_session)

    response = client.get("/api/v1/dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data_source"] == "development"
    assert payload["metrics"][0] == {"label": "Total views", "value": 398_400, "change": None, "detail": None}
    assert payload["creator"]["name"] == "Maya Chen"
    assert payload["creator"]["followers"] == 84_200
    assert payload["insight"]["title"] == "Carousels lead engagement"


def test_empty_dashboard_remains_available_as_a_fallback() -> None:
    dashboard = get_empty_dashboard()

    assert dashboard.data_source == "empty"
    assert dashboard.creator is None
    assert dashboard.recent_content == []
