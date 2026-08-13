from sqlalchemy.orm import Session

from app.db.models.creator_profile import CreatorProfile
from app.domains.content.aggregation import average_cadence_days, share_of_total, strongest_format
from app.domains.content.repository import list_content
from app.domains.creators.repository import get_creator_profile
from app.schemas.dna import (
    DnaEngagementBenchmark,
    DnaFormatPerformance,
    DnaIdentity,
    DnaInsight,
    DnaResponse,
    DnaShare,
)


def get_creator_dna(session: Session, creator_id: str) -> DnaResponse:
    """Return honest, deterministic creative signals derived from persisted content."""
    identity = to_dna_identity(get_creator_profile(session, creator_id))
    posts = list_content(session, creator_id)
    if not posts:
        return DnaResponse(
            data_source="empty",
            identity=identity,
            insights=[
                DnaInsight(
                    title="No published content yet",
                    summary="Import or connect published content with performance data to map your creative pattern.",
                    sample_size=0,
                )
            ],
        )

    total = len(posts)
    platforms = [DnaShare(name=name, count=count, share=share) for name, count, share in share_of_total([post.platform for post in posts])]
    formats = [DnaShare(name=name, count=count, share=share) for name, count, share in share_of_total([post.content_type for post in posts])]
    categories = [DnaShare(name=name, count=count, share=share) for name, count, share in share_of_total([post.category for post in posts])]
    best_format_metric = strongest_format(posts)
    best_format = (
        DnaFormatPerformance(
            name=best_format_metric.name,
            average_engagement_rate=best_format_metric.average_engagement_rate,
            sample_size=best_format_metric.sample_size,
        )
        if best_format_metric is not None
        else None
    )
    benchmark = engagement_benchmark(posts)

    return DnaResponse(
        data_source="development",
        identity=identity,
        total_posts=total,
        platforms=platforms,
        formats=formats,
        categories=categories,
        best_format=best_format,
        engagement_benchmark=benchmark,
        insights=build_insights(posts, total, best_format, platforms),
    )


def to_dna_identity(profile: CreatorProfile | None) -> DnaIdentity | None:
    if profile is None:
        return None
    return DnaIdentity(
        name=profile.name,
        handle=profile.handle,
        niche=profile.niche,
        audience=profile.audience,
        platform=profile.platform,
        follower_count=profile.follower_count,
    )


def engagement_benchmark(posts: list) -> DnaEngagementBenchmark | None:
    rates = [post.engagement_rate for post in posts if post.engagement_rate is not None]
    if not rates:
        return None
    return DnaEngagementBenchmark(
        average_views=round(sum(post.views or 0 for post in posts) / len(posts), 1),
        average_engagement_rate=round(sum(rates) / len(rates), 1),
        sample_size=len(posts),
    )


def build_insights(
    posts: list,
    total: int,
    best_format: DnaFormatPerformance | None,
    platforms: list[DnaShare],
) -> list[DnaInsight]:
    insights: list[DnaInsight] = []
    primary = platforms[0] if platforms else None
    if primary is not None:
        insights.append(
            DnaInsight(
                title=f"{primary.name} is your primary platform",
                summary=f"{primary.count} of {total} published posts ({primary.share}%) live on {primary.name}.",
                evidence=f"Derived from {total} persisted posts.",
                sample_size=total,
            )
        )
    if best_format is not None:
        insights.append(
            DnaInsight(
                title=f"{best_format.name}s lead your engagement",
                summary=f"{best_format.name} posts average {best_format.average_engagement_rate}% engagement across {best_format.sample_size} posts.",
                evidence=f"Based on {best_format.sample_size} posts in this format.",
                sample_size=best_format.sample_size,
            )
        )
    else:
        insights.append(
            DnaInsight(
                title="Format comparison needs more data",
                summary="More posts in the same format are needed before Creator OS can compare what performs best for you.",
                sample_size=None,
            )
        )
    cadence = average_cadence_days(posts)
    if cadence is not None:
        insights.append(
            DnaInsight(
                title=f"You publish about every {cadence} days",
                summary=f"Across {total} dated posts, the average gap between publications is about {cadence} days.",
                evidence=f"Derived from {total} persisted posts.",
                sample_size=total,
            )
        )
    return insights
