from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.domains.dashboard.development_data import DEVELOPMENT_CREATOR_ID
from app.domains.content.intelligence import get_content_intelligence
from app.schemas.content_intelligence import ContentIntelligenceResponse

router = APIRouter()


@router.get("/content-intelligence", response_model=ContentIntelligenceResponse)
def read_content_intelligence(
    creator_id: str = DEVELOPMENT_CREATOR_ID,
    session: Session = Depends(get_db_session),
) -> ContentIntelligenceResponse:
    """Return explainable, deterministic per-post performance analysis."""
    return get_content_intelligence(session, creator_id)
