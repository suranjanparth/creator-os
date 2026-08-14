from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ImportedCreatorProfile(BaseModel):
    """Normalized creator identity delivered by an authorized source."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    handle: str | None = Field(default=None, max_length=255)
    profile_url: str | None = Field(default=None, max_length=500)
    niche: str | None = Field(default=None, max_length=255)
    platform: str | None = Field(default=None, max_length=100)
    audience: str | None = Field(default=None, max_length=255)
    follower_count: int | None = Field(default=None, ge=0)


class CreatorImportRequest(BaseModel):
    """Creator-scoped payload for a normalized creator/content import.

    ``content`` holds raw published-post payloads; each item is validated and
    normalized against the published-content schema during the import so that a
    single malformed post never fails the whole sync.
    """

    model_config = ConfigDict(extra="forbid")

    creator_id: str = Field(min_length=1, max_length=255)
    profile: ImportedCreatorProfile
    content: list[dict] = Field(default_factory=list, max_length=1000)


class ContentItemOutcome(BaseModel):
    id: str
    status: Literal["created", "updated", "skipped", "error"]
    detail: str | None = None


class CreatorImportResponse(BaseModel):
    creator_id: str
    profile_status: Literal["created", "updated", "unchanged"]
    content_received: int
    created: int
    updated: int
    skipped: int
    errors: int
    items: list[ContentItemOutcome]
