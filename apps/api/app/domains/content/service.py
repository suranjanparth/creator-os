from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.content import CreatorContent
from app.domains.content.repository import create_content, list_content
from app.schemas.content import CreatorContentCreate, CreatorContentResponse


def ingest_content(session: Session, content: CreatorContentCreate) -> CreatorContentResponse:
    try:
        record = create_content(session, content)
    except IntegrityError as error:
        session.rollback()
        raise ValueError(f"Content with id '{content.id}' already exists") from error
    return serialize_content(record)


def get_creator_content(session: Session, creator_id: str) -> list[CreatorContentResponse]:
    return [serialize_content(record) for record in list_content(session, creator_id)]


def serialize_content(record: CreatorContent) -> CreatorContentResponse:
    return CreatorContentResponse(
        id=record.id,
        creator_id=record.creator_id,
        platform=record.platform,
        content_type=record.content_type,
        category=record.category,
        title=record.title,
        views=record.views,
        likes=record.likes,
        comments=record.comments,
        shares=record.shares,
        engagement_rate=record.engagement_rate,
        published_at=record.published_at,
    )
