from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class AnalyticsTotals(BaseModel):
    views: int = Field(ge=0)
    likes: int = Field(ge=0)
    comments: int = Field(ge=0)
    shares: int = Field(ge=0)
    engagements: int = Field(ge=0)
    average_engagement_rate: float = Field(ge=0)


class AnalyticsPlatform(BaseModel):
    platform: str
    posts: int = Field(ge=0)
    views: int = Field(ge=0)
    share: float = Field(ge=0, le=100)


class AnalyticsPost(BaseModel):
    id: str
    title: str
    platform: str
    content_type: str
    views: int | None = None
    engagement_rate: float | None = None
    published_at: date | None = None


class AnalyticsTrendPoint(BaseModel):
    date: date
    views: int


class AnalyticsEngagementAnatomy(BaseModel):
    likes_share: float = Field(ge=0, le=100)
    comments_share: float = Field(ge=0, le=100)
    shares_share: float = Field(ge=0, le=100)
    sample_size: int = Field(ge=1)


class AnalyticsResponse(BaseModel):
    data_source: Literal["development", "empty"]
    total_posts: int = Field(default=0, ge=0)
    totals: AnalyticsTotals | None = None
    platform_breakdown: list[AnalyticsPlatform] = Field(default_factory=list)
    top_posts: list[AnalyticsPost] = Field(default_factory=list)
    trend: list[AnalyticsTrendPoint] = Field(default_factory=list)
    engagement_anatomy: AnalyticsEngagementAnatomy | None = None
