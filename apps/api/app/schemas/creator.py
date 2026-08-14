from datetime import datetime

from pydantic import BaseModel, Field


class CreatorProfileCreate(BaseModel):
    creator_id: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    handle: str | None = Field(default=None, max_length=255)
    profile_url: str | None = Field(default=None, max_length=500)
    niche: str | None = Field(default=None, max_length=255)
    platform: str | None = Field(default=None, max_length=100)
    audience: str | None = Field(default=None, max_length=255)
    follower_count: int | None = Field(default=None, ge=0)


class CreatorProfileResponse(CreatorProfileCreate):
    created_at: datetime
    updated_at: datetime
