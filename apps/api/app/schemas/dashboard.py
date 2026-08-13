from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class DashboardCreator(BaseModel):
    name: str
    handle: str | None = None
    niche: str | None = None
    audience: str | None = None
    followers: int | None = None


class DashboardMetric(BaseModel):
    label: str
    value: float | int | None = None
    change: float | None = None
    detail: str | None = None


class DashboardContent(BaseModel):
    id: str
    title: str
    platform: str
    content_type: str
    category: str
    views: int | None = None
    likes: int | None = None
    comments: int | None = None
    shares: int | None = None
    engagement_rate: float | None = None
    published_at: date | None = None


class DashboardTrendPoint(BaseModel):
    date: date
    views: int


class DashboardInsight(BaseModel):
    title: str
    summary: str
    evidence: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    method: str | None = None


class DashboardResponse(BaseModel):
    data_source: Literal["development", "empty"]
    creator: DashboardCreator | None = None
    metrics: list[DashboardMetric] = Field(default_factory=list)
    performance_trend: list[DashboardTrendPoint] = Field(default_factory=list)
    best_performing_content: list[DashboardContent] = Field(default_factory=list)
    recent_content: list[DashboardContent] = Field(default_factory=list)
    insight: DashboardInsight
