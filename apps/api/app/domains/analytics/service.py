from sqlalchemy.orm import Session

from app.db.models.content import CreatorContent
from app.domains.content.aggregation import daily_views_trend
from app.domains.content.repository import list_content
from app.schemas.analytics import (
    AnalyticsEngagementAnatomy,
    AnalyticsPlatform,
    AnalyticsPost,
    AnalyticsResponse,
    AnalyticsTotals,
    AnalyticsTrendPoint,
)


def get_analytics(session: Session, creator_id: str) -> AnalyticsResponse:
    """Return honest, deterministic analytics derived from persisted content."""
    posts = list_content(session, creator_id)
    if not posts:
        return AnalyticsResponse(data_source="empty", total_posts=0)
    return build_analytics(posts)


def build_analytics(posts: list[CreatorContent]) -> AnalyticsResponse:
    total_posts = len(posts)
    total_views = sum(post.views or 0 for post in posts)
    total_likes = sum(post.likes or 0 for post in posts)
    total_comments = sum(post.comments or 0 for post in posts)
    total_shares = sum(post.shares or 0 for post in posts)
    total_engagements = total_likes + total_comments + total_shares

    rates = [post.engagement_rate for post in posts if post.engagement_rate is not None]
    average_engagement_rate = round(sum(rates) / len(rates), 1) if rates else 0.0

    ranked = sorted(posts, key=lambda post: (post.views or 0, post.engagement_rate or 0), reverse=True)

    return AnalyticsResponse(
        data_source="development",
        total_posts=total_posts,
        totals=AnalyticsTotals(
            views=total_views,
            likes=total_likes,
            comments=total_comments,
            shares=total_shares,
            engagements=total_engagements,
            average_engagement_rate=average_engagement_rate,
        ),
        platform_breakdown=build_platform_breakdown(posts, total_views),
        top_posts=[
            AnalyticsPost(
                id=post.id,
                title=post.title,
                platform=post.platform,
                content_type=post.content_type,
                views=post.views,
                engagement_rate=post.engagement_rate,
                published_at=post.published_at,
            )
            for post in ranked[:5]
        ],
        trend=[AnalyticsTrendPoint(date=day, views=views) for day, views in daily_views_trend(posts)],
        engagement_anatomy=(
            AnalyticsEngagementAnatomy(
                likes_share=round(total_likes / total_engagements * 100, 1),
                comments_share=round(total_comments / total_engagements * 100, 1),
                shares_share=round(total_shares / total_engagements * 100, 1),
                sample_size=total_posts,
            )
            if total_engagements
            else None
        ),
    )


def build_platform_breakdown(posts: list[CreatorContent], total_views: int) -> list[AnalyticsPlatform]:
    """Aggregate posts and views per platform, ordered by views descending."""
    by_platform: dict[str, dict[str, int]] = {}
    for post in posts:
        entry = by_platform.setdefault(post.platform, {"posts": 0, "views": 0})
        entry["posts"] += 1
        entry["views"] += post.views or 0
    return [
        AnalyticsPlatform(
            platform=platform,
            posts=entry["posts"],
            views=entry["views"],
            share=round(entry["views"] / total_views * 100, 1) if total_views else 0.0,
        )
        for platform, entry in sorted(by_platform.items(), key=lambda item: item[1]["views"], reverse=True)
    ]
