from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.domains.analytics.service import get_analytics
from app.domains.dashboard.development_data import DEVELOPMENT_CREATOR_ID
from app.schemas.analytics import AnalyticsResponse

router = APIRouter()


@router.get("/analytics", response_model=AnalyticsResponse)
def read_analytics(
    creator_id: str = DEVELOPMENT_CREATOR_ID,
    session: Session = Depends(get_db_session),
) -> AnalyticsResponse:
    """Return creator-scoped analytics derived from persisted content."""
    return get_analytics(session, creator_id)
