from sqlalchemy.orm import Session

from app.domains.content.aggregation import average_cadence_days, strongest_format, top_category, weakest_format
from app.domains.content.repository import list_content
from app.schemas.recommendations import Recommendation, RecommendationOpportunity, RecommendationsResponse


def get_recommendations(session: Session, creator_id: str) -> RecommendationsResponse:
    """Return honest, deterministic next-move recommendations from persisted content."""
    posts = list_content(session, creator_id)
    if not posts:
        return RecommendationsResponse(
            data_source="empty",
            priority_signal="Connect your content to unlock recommendations",
            priority_copy="Creator OS will recommend next moves once published content with performance data is available.",
            total_posts=0,
        )

    total = len(posts)
    strongest = strongest_format(posts)
    weakest = weakest_format(posts)
    category = top_category(posts)
    cadence = average_cadence_days(posts)

    recommendations: list[Recommendation] = []
    if strongest is not None and category is not None:
        recommendations.append(
            Recommendation(
                tag="Post next",
                title=f"Create a {singular_format(strongest.name)} around {category.lower()} topics",
                description=f"Open with the tension your {category.lower()} audience responds to, then deliver one usable takeaway.",
                evidence=f"{strongest.name} posts average {strongest.average_engagement_rate}% engagement across {strongest.sample_size} posts.",
                sample_size=strongest.sample_size,
                action="Create content",
                href="/content",
            )
        )
    if weakest is not None and (strongest is None or weakest.name != strongest.name):
        recommendations.append(
            Recommendation(
                tag="Format test",
                title=f"Retest {format_posts(weakest.name)} with a sharper hook",
                description=f"Reframe this topic as a practical {singular_format(weakest.name)} with a specific audience problem up front.",
                evidence=f"{weakest.name} posts average {weakest.average_engagement_rate}% engagement across {weakest.sample_size} posts.",
                sample_size=weakest.sample_size,
                action="Build draft",
                href="/content",
            )
        )
    if cadence is not None:
        recommendations.append(
            Recommendation(
                tag="Publishing cadence",
                title=f"Publish about every {cadence} days",
                description="A consistent rhythm lets your audience build a habit around your thinking.",
                evidence=f"Average gap between the {total} dated posts.",
                sample_size=total,
                action="Plan schedule",
                href="/content",
            )
        )

    priority_signal = f"{strongest.name}s are your strongest format" if strongest else "Your format mix is still building"
    priority_copy = (
        f"{strongest.name} posts average {strongest.average_engagement_rate}% engagement across {strongest.sample_size} posts — build on what already works."
        if strongest
        else "Add more posts in the same format so Creator OS can compare what performs best for you."
    )

    opportunities: list[RecommendationOpportunity] = []
    if category is not None:
        opportunities.append(
            RecommendationOpportunity(
                title=f"Explore {category.lower()} topics",
                description=f"{category} is your most-published topic and the space your content already occupies.",
                href="/content",
            )
        )
    if weakest is not None:
        opportunities.append(
            RecommendationOpportunity(
                title="Earn the second post",
                description=f"Plan a follow-up to a strong {format_posts(strongest.name) if strongest else 'format'} so your audience can build a habit around your thinking.",
                href="/content-intelligence",
            )
        )

    return RecommendationsResponse(
        data_source="development",
        priority_signal=priority_signal,
        priority_copy=priority_copy,
        recommendations=recommendations,
        opportunities=opportunities,
        total_posts=total,
    )


def singular_format(content_type: str) -> str:
    return content_type.lower()


def format_posts(content_type: str) -> str:
    if content_type.endswith(" post"):
        return f"{content_type[:-5].lower()} posts"
    return f"{content_type.lower()} posts"
