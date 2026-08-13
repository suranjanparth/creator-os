from sqlalchemy.orm import Session

from app.domains.content.repository import get_content
from app.domains.content.service import ingest_content
from app.domains.dashboard.development_data import DEVELOPMENT_CREATOR_ID, DEVELOPMENT_POSTS
from app.schemas.content import CreatorContentCreate


def seed_development_content(session: Session) -> int:
    """Idempotently persist the development posts for local demonstrations."""
    inserted = 0
    for post in DEVELOPMENT_POSTS:
        if get_content(session, post.id) is not None:
            continue
        ingest_content(
            session,
            CreatorContentCreate(creator_id=DEVELOPMENT_CREATOR_ID, **post.model_dump()),
        )
        inserted += 1
    return inserted
