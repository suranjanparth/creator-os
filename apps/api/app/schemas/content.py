from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CreatorContentCreate(BaseModel):
    id: str = Field(min_length=1, max_length=255)
    creator_id: str = Field(min_length=1, max_length=255)
    platform: str = Field(min_length=1, max_length=100)
    url: str | None = Field(default=None, max_length=500)
    content_type: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=255)
    title: str = Field(min_length=1, max_length=500)
    views: int | None = Field(default=None, ge=0)
    likes: int | None = Field(default=None, ge=0)
    comments: int | None = Field(default=None, ge=0)
    shares: int | None = Field(default=None, ge=0)
    saves: int | None = Field(default=None, ge=0)
    reach: int | None = Field(default=None, ge=0)
    impressions: int | None = Field(default=None, ge=0)
    engagement_rate: float | None = Field(default=None, ge=0)
    published_at: date | None = None


class CreatorContentResponse(CreatorContentCreate):
    pass


class ContentIngestItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=255)
    platform: str = Field(min_length=1, max_length=100)
    url: str | None = Field(default=None, max_length=500)
    content_type: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=255)
    title: str = Field(min_length=1, max_length=500)
    views: int | None = Field(default=None, ge=0)
    likes: int | None = Field(default=None, ge=0)
    comments: int | None = Field(default=None, ge=0)
    shares: int | None = Field(default=None, ge=0)
    saves: int | None = Field(default=None, ge=0)
    reach: int | None = Field(default=None, ge=0)
    impressions: int | None = Field(default=None, ge=0)
    engagement_rate: float | None = Field(default=None, ge=0)
    published_at: date | None = None


class ContentIngestRequest(BaseModel):
    creator_id: str = Field(min_length=1, max_length=255)
    items: list[ContentIngestItem] = Field(min_length=1, max_length=1000)


class ContentIngestItemResult(BaseModel):
    id: str
    status: Literal["created", "skipped"]
    detail: str | None = None


class ContentIngestResponse(BaseModel):
    creator_id: str
    received: int
    created: int
    skipped: int
    items: list[ContentIngestItemResult]
