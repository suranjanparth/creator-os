from sqlalchemy.orm import Session

from app.db.models.creator_profile import CreatorProfile
from app.schemas.creator import CreatorProfileCreate


def create_creator_profile(session: Session, profile: CreatorProfileCreate) -> CreatorProfile:
    record = CreatorProfile(**profile.model_dump())
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def get_creator_profile(session: Session, creator_id: str) -> CreatorProfile | None:
    return session.get(CreatorProfile, creator_id)


def list_creator_profiles(session: Session) -> list[CreatorProfile]:
    return list(session.query(CreatorProfile).order_by(CreatorProfile.name, CreatorProfile.creator_id))


def update_creator_profile(session: Session, creator_id: str, values: dict) -> CreatorProfile | None:
    record = session.get(CreatorProfile, creator_id)
    if record is None:
        return None
    for key, value in values.items():
        setattr(record, key, value)
    session.commit()
    session.refresh(record)
    return record
