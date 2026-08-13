from typing import Literal

from pydantic import BaseModel, Field


class DnaIdentity(BaseModel):
    name: str
    handle: str | None = None
    niche: str | None = None
    audience: str | None = None
    platform: str | None = None
    follower_count: int | None = None


class DnaShare(BaseModel):
    name: str
    count: int = Field(ge=0)
    share: float = Field(ge=0, le=100)


class DnaFormatPerformance(BaseModel):
    name: str
    average_engagement_rate: float = Field(ge=0)
    sample_size: int = Field(ge=1)


class DnaEngagementBenchmark(BaseModel):
    average_views: float = Field(ge=0)
    average_engagement_rate: float = Field(ge=0)
    sample_size: int = Field(ge=1)


class DnaInsight(BaseModel):
    title: str
    summary: str
    evidence: str | None = None
    sample_size: int | None = None


class DnaResponse(BaseModel):
    data_source: Literal["development", "empty"]
    identity: DnaIdentity | None = None
    total_posts: int = Field(default=0, ge=0)
    platforms: list[DnaShare] = Field(default_factory=list)
    formats: list[DnaShare] = Field(default_factory=list)
    categories: list[DnaShare] = Field(default_factory=list)
    best_format: DnaFormatPerformance | None = None
    engagement_benchmark: DnaEngagementBenchmark | None = None
    insights: list[DnaInsight] = Field(default_factory=list)
