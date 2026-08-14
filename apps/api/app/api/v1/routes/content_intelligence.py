from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.domains.content.intelligence import get_content_intelligence
from app.schemas.content_intelligence import ContentIntelligenceResponse

router = APIRouter()


@router.get("/content-intelligence", response_model=ContentIntelligenceResponse)
def read_content_intelligence(
    creator_id: str,
    session: Session = Depends(get_db_session),
) -> ContentIntelligenceResponse:
    """Return explainable, deterministic per-post performance analysis."""
    if not creator_id or not creator_id.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="creator_id is required")
    return get_content_intelligence(session, creator_id)
