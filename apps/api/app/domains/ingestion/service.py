from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.domains.content.repository import create_content, get_content, update_content
from app.domains.creators.repository import create_creator_profile, get_creator_profile, update_creator_profile
from app.schemas.content import ContentIngestItem, CreatorContentCreate
from app.schemas.creator import CreatorProfileCreate
from app.schemas.ingestion import (
    ContentItemOutcome,
    CreatorImportRequest,
    CreatorImportResponse,
    ImportedCreatorProfile,
)

_PROFILE_FIELDS = ("name", "handle", "niche", "platform", "audience", "follower_count")
_CONTENT_FIELDS = (
    "id",
    "platform",
    "content_type",
    "category",
    "title",
    "views",
    "likes",
    "comments",
    "shares",
    "engagement_rate",
    "published_at",
)


def import_creator(session: Session, request: CreatorImportRequest) -> CreatorImportResponse:
    """Persist an authorized creator profile and their published content idempotently.

    The profile is upserted (created or updated) under the request's creator id.
    Content items are normalized individually so a malformed post is reported as
    an ``error`` outcome instead of failing the whole import. Re-importing the
    same normalized payload never creates duplicates.
    """
    profile_status, _ = upsert_profile(session, request.creator_id, request.profile)

    outcomes: list[ContentItemOutcome] = []
    created = updated = skipped = errors = 0

    for raw_item in request.content:
        try:
            item = ContentIngestItem.model_validate(raw_item)
        except ValidationError as error:
            outcomes.append(
                ContentItemOutcome(
                    id=str(raw_item.get("id", "")),
                    status="error",
                    detail=_first_validation_error(error),
                )
            )
            errors += 1
            continue

        outcome = upsert_content(session, request.creator_id, item)
        outcomes.append(outcome)
        if outcome.status == "created":
            created += 1
        elif outcome.status == "updated":
            updated += 1
        elif outcome.status == "skipped":
            skipped += 1

    return CreatorImportResponse(
        creator_id=request.creator_id,
        profile_status=profile_status,
        content_received=len(request.content),
        created=created,
        updated=updated,
        skipped=skipped,
        errors=errors,
        items=outcomes,
    )


def upsert_profile(session: Session, creator_id: str, profile: ImportedCreatorProfile) -> tuple[str, object]:
    """Create or update a creator profile, returning its outcome status."""
    existing = get_creator_profile(session, creator_id)
    values = profile.model_dump()

    if existing is None:
        create_creator_profile(session, CreatorProfileCreate(creator_id=creator_id, **values))
        return "created", existing

    if _values_match(existing, values, _PROFILE_FIELDS):
        return "unchanged", existing

    update_creator_profile(session, creator_id, values)
    return "updated", existing


def upsert_content(session: Session, creator_id: str, item: ContentIngestItem) -> ContentItemOutcome:
    """Create, update, or skip one content record based on its persisted state."""
    existing = get_content(session, item.id)

    if existing is None:
        create_content(session, CreatorContentCreate(creator_id=creator_id, **item.model_dump()))
        return ContentItemOutcome(id=item.id, status="created")

    if _values_match(existing, item.model_dump(), _CONTENT_FIELDS):
        return ContentItemOutcome(id=item.id, status="skipped", detail="already up to date")

    update_content(session, item.id, {field: value for field, value in item.model_dump().items() if field != "id"})
    return ContentItemOutcome(id=item.id, status="updated")


def _values_match(record: object, values: dict, fields: tuple[str, ...]) -> bool:
    return all(getattr(record, field) == values.get(field) for field in fields)


def _first_validation_error(error: ValidationError) -> str:
    first = error.errors()[0]
    location = ".".join(str(part) for part in first.get("loc", ()))
    return f"invalid at {location}: {first.get('msg', 'invalid value')}" if location else str(first.get("msg", "invalid value"))
