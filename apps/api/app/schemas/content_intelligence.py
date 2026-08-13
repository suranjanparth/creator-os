from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.dashboard import DashboardContent


PerformanceTier = Literal["Excellent", "Strong", "Average", "Weak"]


class ContentIntelligenceItem(BaseModel):
    content: DashboardContent
    performance_score: int = Field(ge=0, le=100)
    performance_tier: PerformanceTier
    primary_reason: str
    detected_pattern: str
    recommended_next_action: str


class FormatPerformance(BaseModel):
    name: str
    average_score: float
    sample_size: int


class ContentIntelligenceSummary(BaseModel):
    strongest_content_format: FormatPerformance | None = None
    weakest_content_format: FormatPerformance | None = None
    strongest_engagement_driver: str | None = None
    recommended_content_direction: str | None = None


class ContentIntelligenceResponse(BaseModel):
    data_source: Literal["development", "empty"]
    method: str
    summary: ContentIntelligenceSummary | None = None
    items: list[ContentIntelligenceItem] = Field(default_factory=list)
