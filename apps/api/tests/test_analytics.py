from app.domains.analytics.service import get_analytics
from app.domains.content.seed import seed_development_content
from app.domains.dashboard.development_data import DEVELOPMENT_CREATOR_ID


def test_analytics_returns_honest_empty_state(db_session) -> None:
    analytics = get_analytics(db_session, "unknown-creator")

    assert analytics.data_source == "empty"
    assert analytics.total_posts == 0
    assert analytics.totals is None
    assert analytics.platform_breakdown == []
    assert analytics.top_posts == []
    assert analytics.engagement_anatomy is None


def test_analytics_is_derived_from_persisted_seeded_content(db_session) -> None:
    seed_development_content(db_session)

    analytics = get_analytics(db_session, DEVELOPMENT_CREATOR_ID)

    assert analytics.data_source == "development"
    assert analytics.total_posts == 6

    assert analytics.totals is not None
    assert analytics.totals.views == 398_400
    assert analytics.totals.likes == 27_030
    assert analytics.totals.comments == 2_183
    assert analytics.totals.shares == 7_604
    assert analytics.totals.engagements == 36_817
    assert analytics.totals.average_engagement_rate == 9.0

    assert [platform.platform for platform in analytics.platform_breakdown] == ["Instagram", "TikTok", "LinkedIn"]
    instagram = analytics.platform_breakdown[0]
    assert instagram.posts == 3
    assert instagram.views == 243_200
    assert instagram.share == 61.0

    assert analytics.top_posts[0].id == "maya-creative-reset"
    assert len(analytics.trend) == 6
    assert analytics.trend[0].date.isoformat() == "2026-07-27"

    assert analytics.engagement_anatomy is not None
    assert analytics.engagement_anatomy.likes_share == 73.4
    assert analytics.engagement_anatomy.comments_share == 5.9
    assert analytics.engagement_anatomy.shares_share == 20.7


def test_analytics_is_scoped_to_the_creator(db_session) -> None:
    seed_development_content(db_session)

    other = get_analytics(db_session, "another-creator")

    assert other.data_source == "empty"
    assert other.total_posts == 0


def test_analytics_endpoint_returns_response_contract(client, db_session) -> None:
    seed_development_content(db_session)

    response = client.get("/api/v1/analytics")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data_source"] == "development"
    assert payload["total_posts"] == 6
    assert payload["totals"]["views"] == 398_400
    assert payload["platform_breakdown"][0]["platform"] == "Instagram"
    assert payload["top_posts"][0]["id"] == "maya-creative-reset"
    assert payload["engagement_anatomy"]["likes_share"] == 73.4


def test_analytics_endpoint_empty_state_contract(client) -> None:
    response = client.get("/api/v1/analytics", params={"creator_id": "no-such-creator"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["data_source"] == "empty"
    assert payload["total_posts"] == 0
    assert payload["totals"] is None
