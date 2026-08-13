from collections import defaultdict
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db.models.content import CreatorContent
from app.db.models.creator_profile import CreatorProfile
from app.domains.content.repository import list_content
from app.domains.creators.repository import get_creator_profile
from app.schemas.content_intelligence import (
    ContentIntelligenceItem,
    ContentIntelligenceResponse,
    ContentIntelligenceSummary,
    FormatPerformance,
    PerformanceTier,
)
from app.schemas.dashboard import DashboardContent

DATASET_LABEL = "for this creator's posts"


@dataclass(frozen=True)
class PerformanceBaselines:
    average_views: float
    average_engagement_rate: float
    average_share_rate: float
    average_comment_rate: float


def get_content_intelligence(session: Session, creator_id: str) -> ContentIntelligenceResponse:
    """Return deterministic per-post intelligence for persisted creator content."""
    posts = tuple(to_dashboard_content(record) for record in list_content(session, creator_id))
    if not posts:
        return get_empty_content_intelligence()

    profile = get_creator_profile(session, creator_id)
    comparison_label = f"{profile.name}'s average" if profile else "this creator's average"

    baselines = calculate_baselines(posts)
    items = [analyze_content(post, baselines, comparison_label) for post in posts]
    return ContentIntelligenceResponse(
        data_source="development",
        method=method_for(profile),
        summary=build_summary(items, baselines, DATASET_LABEL),
        items=sorted(items, key=lambda item: item.performance_score, reverse=True),
    )


def method_for(profile: CreatorProfile | None) -> str:
    if profile is not None:
        return f"Initial rule-based intelligence layer. Scores compare each post with {profile.name}'s persisted creator averages."
    return "Initial rule-based intelligence layer. Scores compare each post with this creator's averages."


def to_dashboard_content(record: CreatorContent) -> DashboardContent:
    return DashboardContent(
        id=record.id,
        title=record.title,
        platform=record.platform,
        content_type=record.content_type,
        category=record.category,
        views=record.views,
        likes=record.likes,
        comments=record.comments,
        shares=record.shares,
        engagement_rate=record.engagement_rate,
        published_at=record.published_at,
    )


def get_empty_content_intelligence() -> ContentIntelligenceResponse:
    """Keep a no-data response ready until persisted creator data is connected."""
    return ContentIntelligenceResponse(
        data_source="empty",
        method="Initial rule-based intelligence layer. Connect creator data to generate content analysis.",
    )


def calculate_baselines(posts: tuple[DashboardContent, ...]) -> PerformanceBaselines:
    return PerformanceBaselines(
        average_views=sum(post.views or 0 for post in posts) / len(posts),
        average_engagement_rate=sum(post.engagement_rate or 0 for post in posts) / len(posts),
        average_share_rate=sum(rate(post.shares, post.views) for post in posts) / len(posts),
        average_comment_rate=sum(rate(post.comments, post.views) for post in posts) / len(posts),
    )


def calculate_performance_score(post: DashboardContent, baselines: PerformanceBaselines) -> int:
    """Weight normalized reach and engagement signals, capped at 150% of baseline."""
    score = (
        normalized(post.views or 0, baselines.average_views, 35)
        + normalized(post.engagement_rate or 0, baselines.average_engagement_rate, 35)
        + normalized(rate(post.shares, post.views), baselines.average_share_rate, 20)
        + normalized(rate(post.comments, post.views), baselines.average_comment_rate, 10)
    )
    return round(score)


def analyze_content(post: DashboardContent, baselines: PerformanceBaselines, comparison_label: str) -> ContentIntelligenceItem:
    score = calculate_performance_score(post, baselines)
    tier = performance_tier(score)
    signals = {
        "Views": ratio(post.views or 0, baselines.average_views),
        "Engagement": ratio(post.engagement_rate or 0, baselines.average_engagement_rate),
        "Shares": ratio(rate(post.shares, post.views), baselines.average_share_rate),
        "Comments": ratio(rate(post.comments, post.views), baselines.average_comment_rate),
    }
    signal_name, signal_ratio = max(signals.items(), key=lambda item: item[1])
    primary_reason = describe_primary_reason(signal_name, signal_ratio, comparison_label)

    return ContentIntelligenceItem(
        content=post,
        performance_score=score,
        performance_tier=tier,
        primary_reason=primary_reason,
        detected_pattern=detect_pattern(post, score, signals),
        recommended_next_action=recommend_next_action(post, tier),
    )


def performance_tier(score: int) -> PerformanceTier:
    if score >= 80:
        return "Excellent"
    if score >= 65:
        return "Strong"
    if score >= 45:
        return "Average"
    return "Weak"


def build_summary(items: list[ContentIntelligenceItem], baselines: PerformanceBaselines, dataset_label: str) -> ContentIntelligenceSummary:
    by_format: dict[str, list[int]] = defaultdict(list)
    by_category: dict[str, list[int]] = defaultdict(list)
    for item in items:
        by_format[item.content.content_type].append(item.performance_score)
        by_category[item.content.category].append(item.performance_score)

    comparable_formats = {name: scores for name, scores in by_format.items() if len(scores) >= 2}
    if not comparable_formats:
        return ContentIntelligenceSummary()

    strongest_name, strongest_scores = max(comparable_formats.items(), key=lambda item: sum(item[1]) / len(item[1]))
    weakest_name, weakest_scores = min(comparable_formats.items(), key=lambda item: sum(item[1]) / len(item[1]))
    strongest_category = max(by_category.items(), key=lambda item: sum(item[1]) / len(item[1]))[0]
    driver = max(
        {
            "Likes": sum(rate(item.content.likes, item.content.views) for item in items),
            "Comments": sum(rate(item.content.comments, item.content.views) for item in items),
            "Shares": sum(rate(item.content.shares, item.content.views) for item in items),
        }.items(),
        key=lambda item: item[1],
    )[0]

    return ContentIntelligenceSummary(
        strongest_content_format=format_performance(strongest_name, strongest_scores),
        weakest_content_format=format_performance(weakest_name, weakest_scores),
        strongest_engagement_driver=f"{driver} are the largest interaction source {dataset_label}.",
        recommended_content_direction=(
            f"Prioritize {format_posts(strongest_name)} around {strongest_category.lower()} topics, "
            f"then test a clearer hook on {format_posts(weakest_name)}."
        ),
    )


def format_performance(name: str, scores: list[int]) -> FormatPerformance:
    return FormatPerformance(name=name, average_score=round(sum(scores) / len(scores), 1), sample_size=len(scores))


def format_posts(content_type: str) -> str:
    if content_type.endswith(" post"):
        return f"{content_type[:-5].lower()} posts"
    return f"{content_type.lower()} posts"


def detect_pattern(post: DashboardContent, score: int, signals: dict[str, float]) -> str:
    if signals["Shares"] >= 1.15:
        return "Save-and-share framework"
    if signals["Comments"] >= 1.15:
        return "Conversation-led perspective"
    if score >= 65:
        return "Above-average audience response"
    return "Limited distribution signal"


def recommend_next_action(post: DashboardContent, tier: PerformanceTier) -> str:
    if tier in {"Excellent", "Strong"}:
        return f"Create a follow-up {post.content_type.lower()} using the same {post.category.lower()} angle."
    if tier == "Average":
        return f"Retest this {post.content_type.lower()} with a sharper opening hook and a shareable takeaway."
    return f"Reframe this topic as a practical {post.content_type.lower()} with a specific audience problem up front."


def describe_primary_reason(signal_name: str, signal_ratio: float, comparison_label: str) -> str:
    difference = round(abs(signal_ratio - 1) * 100)
    direction = "above" if signal_ratio >= 1 else "below"
    verb = "is" if signal_name == "Engagement" else "are"
    return f"{signal_name} {verb} {difference}% {direction} {comparison_label}."


def normalized(value: float, average: float, weight: float) -> float:
    return min(ratio(value, average), 1.5) / 1.5 * weight


def ratio(value: float, average: float) -> float:
    return value / average if average else 0


def rate(interactions: int | None, views: int | None) -> float:
    return (interactions or 0) / views if views else 0
