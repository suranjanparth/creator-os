from collections import defaultdict
from datetime import date

from sqlalchemy.orm import Session

from app.db.models.content import CreatorContent
from app.db.models.creator_profile import CreatorProfile
from app.domains.content.aggregation import daily_views_trend
from app.domains.content.repository import list_content
from app.domains.creators.repository import get_creator_profile
from app.schemas.dashboard import (
    DashboardContent,
    DashboardCreator,
    DashboardInsight,
    DashboardMetric,
    DashboardResponse,
    DashboardTrendPoint,
)


def get_dashboard(session: Session, creator_id: str) -> DashboardResponse:
    """Return a creator-scoped dashboard derived from persisted content."""
    creator = to_dashboard_creator(get_creator_profile(session, creator_id))
    posts = list_content(session, creator_id)
    if not posts:
        return get_empty_dashboard(creator=creator)
    return build_dashboard(posts, creator)


def build_dashboard(posts: list[CreatorContent], creator: DashboardCreator | None) -> DashboardResponse:
    content = [to_dashboard_content(post) for post in posts]
    total_views = sum(post.views or 0 for post in content)
    total_engagements = sum((post.likes or 0) + (post.comments or 0) + (post.shares or 0) for post in content)
    engagement_rate = round(total_engagements / total_views * 100, 1) if total_views else 0

    return DashboardResponse(
        data_source="development",
        creator=creator,
        metrics=[
            DashboardMetric(label="Total views", value=total_views),
            DashboardMetric(label="Engagement rate", value=engagement_rate),
            DashboardMetric(label="Total content", value=len(content)),
        ],
        performance_trend=build_trend(content),
        best_performing_content=sorted(content, key=lambda post: post.engagement_rate or 0, reverse=True)[:3],
        recent_content=sorted(content, key=lambda post: post.published_at or date.min, reverse=True)[:4],
        insight=build_insight(content),
    )


def to_dashboard_creator(profile: CreatorProfile | None) -> DashboardCreator | None:
    """Map a persisted creator profile to the dashboard creator shape."""
    if profile is None:
        return None
    return DashboardCreator(
        name=profile.name,
        handle=profile.handle,
        niche=profile.niche,
        audience=profile.audience,
        followers=profile.follower_count,
    )


def build_trend(posts: list[DashboardContent]) -> list[DashboardTrendPoint]:
    """Daily views bucketed by each post's published date."""
    return [DashboardTrendPoint(date=day, views=views) for day, views in daily_views_trend(posts)]


def build_insight(posts: list[DashboardContent]) -> DashboardInsight:
    rates_by_format: dict[str, list[float]] = defaultdict(list)
    for post in posts:
        if post.engagement_rate is not None:
            rates_by_format[post.content_type].append(post.engagement_rate)

    comparable = {name: rates for name, rates in rates_by_format.items() if len(rates) >= 2}
    if not comparable:
        return DashboardInsight(
            title="Not enough format data yet",
            summary="More posts in the same format are needed before Creator OS can compare format performance.",
            method="Initial intelligence layer: deterministic format-performance rule.",
        )

    strongest_name, strongest_rates = max(comparable.items(), key=lambda item: sum(item[1]) / len(item[1]))
    average_rate = round(sum(strongest_rates) / len(strongest_rates), 1)

    return DashboardInsight(
        title=f"{strongest_name}s lead engagement",
        summary=(
            f"{strongest_name} posts average {average_rate}% engagement across {len(strongest_rates)} posts, "
            "making them the strongest format to build on next."
        ),
        evidence=f"Based on {len(strongest_rates)} {strongest_name.lower()} posts across {len(posts)} posts.",
        confidence=round(len(strongest_rates) / len(posts), 2),
        method="Initial intelligence layer: deterministic format-performance rule.",
    )


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


def get_empty_dashboard(creator: DashboardCreator | None = None) -> DashboardResponse:
    """Provide a safe fallback before persisted creator content is available."""
    return DashboardResponse(
        data_source="empty",
        creator=creator,
        insight=DashboardInsight(
            title="Connect your creator data to unlock insights",
            summary="Creator OS will surface performance patterns and recommendations once published content and audience data are available.",
        ),
    )
