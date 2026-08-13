from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.content import CreatorContent
from app.schemas.content import CreatorContentCreate


def create_content(session: Session, content: CreatorContentCreate) -> CreatorContent:
    record = CreatorContent(**content.model_dump())
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def list_content(session: Session, creator_id: str) -> list[CreatorContent]:
    statement = select(CreatorContent).where(CreatorContent.creator_id == creator_id).order_by(CreatorContent.published_at.desc(), CreatorContent.id)
    return list(session.scalars(statement))


def get_content(session: Session, content_id: str) -> CreatorContent | None:
    return session.get(CreatorContent, content_id)


def update_content(session: Session, content_id: str, values: dict) -> CreatorContent | None:
    record = session.get(CreatorContent, content_id)
    if record is None:
        return None
    for key, value in values.items():
        setattr(record, key, value)
    session.commit()
    session.refresh(record)
    return record
