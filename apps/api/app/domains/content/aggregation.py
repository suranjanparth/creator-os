from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class FormatMetric:
    name: str
    average_engagement_rate: float
    sample_size: int


def share_of_total(names: list[str]) -> list[tuple[str, int, float]]:
    """Return (name, count, percentage) tuples ordered most common first."""
    counts = Counter(names)
    total = len(names) or 1
    return [(name, count, round(count / total * 100, 1)) for name, count in counts.most_common()]


def daily_views_trend(posts: list) -> list[tuple[date, int]]:
    """Daily views bucketed by each post's published date, ordered oldest first."""
    daily: dict[date, int] = defaultdict(int)
    for post in posts:
        if post.published_at is not None:
            daily[post.published_at] += post.views or 0
    return sorted(daily.items())


def comparable_formats(posts: list, min_sample: int = 2) -> dict[str, list[float]]:
    """Group engagement rates by content type, keeping formats with enough posts."""
    rates: dict[str, list[float]] = defaultdict(list)
    for post in posts:
        if post.engagement_rate is not None:
            rates[post.content_type].append(post.engagement_rate)
    return {name: values for name, values in rates.items() if len(values) >= min_sample}


def strongest_format(posts: list) -> FormatMetric | None:
    comparable = comparable_formats(posts)
    if not comparable:
        return None
    name, rates = max(comparable.items(), key=lambda item: sum(item[1]) / len(item[1]))
    return FormatMetric(name=name, average_engagement_rate=round(sum(rates) / len(rates), 1), sample_size=len(rates))


def weakest_format(posts: list) -> FormatMetric | None:
    comparable = comparable_formats(posts)
    if not comparable:
        return None
    name, rates = min(comparable.items(), key=lambda item: sum(item[1]) / len(item[1]))
    return FormatMetric(name=name, average_engagement_rate=round(sum(rates) / len(rates), 1), sample_size=len(rates))


def top_category(posts: list) -> str | None:
    counts = Counter(post.category for post in posts if post.category)
    return counts.most_common(1)[0][0] if counts else None


def average_cadence_days(posts: list) -> int | None:
    """Average gap in days between unique published dates, when at least two exist."""
    dates = sorted({post.published_at for post in posts if post.published_at is not None})
    if len(dates) < 2:
        return None
    gaps = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    return round(sum(gaps) / len(gaps))
