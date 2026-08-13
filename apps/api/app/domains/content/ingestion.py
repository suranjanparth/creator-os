from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domains.content.repository import create_content, get_content
from app.schemas.content import (
    ContentIngestItemResult,
    ContentIngestRequest,
    ContentIngestResponse,
    CreatorContentCreate,
)


def ingest_content_batch(session: Session, request: ContentIngestRequest) -> ContentIngestResponse:
    """Persist a creator-scoped batch of content, skipping duplicates safely.

    Ownership is explicit at the request level: every item is written under the
    request's ``creator_id`` and items cannot declare their own creator, so
    cross-creator writes are prevented by construction.
    """
    results: list[ContentIngestItemResult] = []
    created = 0
    skipped = 0

    for item in request.items:
        if get_content(session, item.id) is not None:
            results.append(ContentIngestItemResult(id=item.id, status="skipped", detail="already exists"))
            skipped += 1
            continue
        try:
            create_content(
                session,
                CreatorContentCreate(creator_id=request.creator_id, **item.model_dump()),
            )
        except IntegrityError:
            session.rollback()
            results.append(ContentIngestItemResult(id=item.id, status="skipped", detail="already exists"))
            skipped += 1
            continue
        results.append(ContentIngestItemResult(id=item.id, status="created"))
        created += 1

    return ContentIngestResponse(
        creator_id=request.creator_id,
        received=len(request.items),
        created=created,
        skipped=skipped,
        items=results,
    )
