from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.creator_profile import CreatorProfile
from app.domains.creators.repository import create_creator_profile, list_creator_profiles
from app.schemas.creator import CreatorProfileCreate, CreatorProfileResponse


def save_creator_profile(session: Session, profile: CreatorProfileCreate) -> CreatorProfileResponse:
    """Persist a creator profile, rejecting duplicate creator identities."""
    try:
        record = create_creator_profile(session, profile)
    except IntegrityError as error:
        session.rollback()
        raise ValueError(f"Creator profile for '{profile.creator_id}' already exists") from error
    return serialize_creator_profile(record)


def serialize_creator_profile(record: CreatorProfile) -> CreatorProfileResponse:
    return CreatorProfileResponse(
        creator_id=record.creator_id,
        name=record.name,
        handle=record.handle,
        profile_url=record.profile_url,
        niche=record.niche,
        platform=record.platform,
        audience=record.audience,
        follower_count=record.follower_count,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def get_creator_profiles(session: Session) -> list[CreatorProfileResponse]:
    return [serialize_creator_profile(record) for record in list_creator_profiles(session)]
