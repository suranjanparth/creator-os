from typing import Literal

from pydantic import BaseModel, Field


class Recommendation(BaseModel):
    tag: str
    title: str
    description: str
    evidence: str | None = None
    sample_size: int | None = None
    action: str
    href: str | None = None


class RecommendationOpportunity(BaseModel):
    title: str
    description: str
    href: str


class RecommendationsResponse(BaseModel):
    data_source: Literal["development", "empty"]
    priority_signal: str
    priority_copy: str
    recommendations: list[Recommendation] = Field(default_factory=list)
    opportunities: list[RecommendationOpportunity] = Field(default_factory=list)
    total_posts: int = Field(default=0, ge=0)
