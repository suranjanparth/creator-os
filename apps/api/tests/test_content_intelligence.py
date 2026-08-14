from app.domains.content.intelligence import (
    analyze_content,
    build_summary,
    calculate_baselines,
    calculate_performance_score,
    get_content_intelligence,
    performance_tier,
)
from app.domains.content.repository import create_content
from app.domains.content.seed import seed_development_content
from app.domains.creators.seed import seed_development_creator_profile
from app.domains.dashboard.development_data import DEVELOPMENT_CREATOR_ID, DEVELOPMENT_POSTS
from app.schemas.content import CreatorContentCreate


def test_performance_score_uses_creator_average_comparison() -> None:
    baselines = calculate_baselines(DEVELOPMENT_POSTS)

    strongest_post = DEVELOPMENT_POSTS[2]
    weakest_post = DEVELOPMENT_POSTS[4]

    assert calculate_performance_score(strongest_post, baselines) == 79
    assert calculate_performance_score(weakest_post, baselines) == 43


def test_performance_tier_boundaries_are_explainable() -> None:
    assert performance_tier(80) == "Excellent"
    assert performance_tier(65) == "Strong"
    assert performance_tier(45) == "Average"
    assert performance_tier(44) == "Weak"


def test_summary_is_empty_when_no_format_has_enough_posts() -> None:
    post = DEVELOPMENT_POSTS[0]
    baselines = calculate_baselines((post,))
    item = analyze_content(post, baselines, "Maya Chen's average")

    assert build_summary([item], baselines, "for this creator's posts").model_dump() == {
        "strongest_content_format": None,
        "weakest_content_format": None,
        "strongest_engagement_driver": None,
        "recommended_content_direction": None,
    }


def test_content_intelligence_uses_persisted_seeded_data(db_session) -> None:
    seed_development_creator_profile(db_session)
    seed_development_content(db_session)

    intelligence = get_content_intelligence(db_session, DEVELOPMENT_CREATOR_ID)

    assert intelligence.data_source == "development"
    assert intelligence.method == "Initial rule-based intelligence layer. Scores compare each post with Maya Chen's persisted creator averages."
    assert intelligence.summary.model_dump() == {
        "strongest_content_format": {"name": "Carousel", "average_score": 71.5, "sample_size": 2},
        "weakest_content_format": {"name": "Text post", "average_score": 46.0, "sample_size": 2},
        "strongest_engagement_driver": "Likes are the largest interaction source for this creator's posts.",
        "recommended_content_direction": "Prioritize carousel posts around creative practice topics, then test a clearer hook on text posts.",
    }
    assert intelligence.items[0].content.id == "maya-workflow-energy"
    assert intelligence.items[0].performance_tier == "Strong"
    assert "Maya Chen's average" in intelligence.items[0].primary_reason
    assert intelligence.items[-1].performance_tier == "Weak"
    assert intelligence.items[-1].detected_pattern == "Conversation-led perspective"


def test_content_intelligence_endpoint_returns_persisted_seeded_output(client, db_session) -> None:
    seed_development_content(db_session)

    response = client.get("/api/v1/content-intelligence", params={"creator_id": DEVELOPMENT_CREATOR_ID})

    assert response.status_code == 200
    intelligence = response.json()
    assert intelligence["data_source"] == "development"
    assert intelligence["summary"]["strongest_content_format"] == {
        "name": "Carousel",
        "average_score": 71.5,
        "sample_size": 2,
    }
    assert intelligence["items"][0]["content"]["id"] == "maya-workflow-energy"


def test_content_intelligence_empty_dataset_returns_honest_empty_state(db_session) -> None:
    intelligence = get_content_intelligence(db_session, DEVELOPMENT_CREATOR_ID)

    assert intelligence.data_source == "empty"
    assert intelligence.items == []
    assert intelligence.summary is None


def test_content_intelligence_insufficient_dataset_does_not_crash(db_session) -> None:
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

    intelligence = get_content_intelligence(db_session, DEVELOPMENT_CREATOR_ID)

    assert len(intelligence.items) == 1
    assert intelligence.summary is not None
    assert intelligence.summary.strongest_content_format is None
    assert intelligence.summary.weakest_content_format is None
    assert intelligence.summary.strongest_engagement_driver is None
    assert intelligence.summary.recommended_content_direction is None


def test_content_intelligence_uses_persisted_profile_for_comparison_label(db_session) -> None:
    from app.schemas.creator import CreatorProfileCreate
    from app.domains.creators.repository import create_creator_profile

    create_creator_profile(
        db_session,
        CreatorProfileCreate(
            creator_id="creator-pro",
            name="Alex Rivera",
            handle="@alexwrites",
            niche="Business storytelling",
        ),
    )
    create_content(
        db_session,
        CreatorContentCreate(
            id="pro-post",
            creator_id="creator-pro",
            platform="LinkedIn",
            content_type="Text post",
            category="Business storytelling",
            title="A profile-scoped post",
            views=5_000,
            likes=400,
            comments=50,
            shares=100,
            engagement_rate=9.0,
        ),
    )

    intelligence = get_content_intelligence(db_session, "creator-pro")

    assert intelligence.data_source == "development"
    assert "Alex Rivera's average" in intelligence.items[0].primary_reason
    assert "Alex Rivera's persisted creator averages" in intelligence.method
