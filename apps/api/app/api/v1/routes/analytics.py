from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.domains.analytics.service import get_analytics
from app.schemas.analytics import AnalyticsResponse

router = APIRouter()


@router.get("/analytics", response_model=AnalyticsResponse)
def read_analytics(
    creator_id: str,
    session: Session = Depends(get_db_session),
) -> AnalyticsResponse:
    """Return creator-scoped analytics derived from persisted content."""
    if not creator_id or not creator_id.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="creator_id is required")
    return get_analytics(session, creator_id)
