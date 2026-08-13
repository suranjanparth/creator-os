from sqlalchemy.orm import Session

from app.domains.creators.development_data import DEVELOPMENT_CREATOR_PROFILE
from app.domains.creators.repository import get_creator_profile
from app.domains.creators.service import save_creator_profile


def seed_development_creator_profile(session: Session) -> int:
    """Idempotently persist the development creator identity profile."""
    if get_creator_profile(session, DEVELOPMENT_CREATOR_PROFILE.creator_id) is not None:
        return 0
    save_creator_profile(session, DEVELOPMENT_CREATOR_PROFILE)
    return 1
