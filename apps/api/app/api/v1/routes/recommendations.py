from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.domains.recommendations.service import get_recommendations
from app.schemas.recommendations import RecommendationsResponse

router = APIRouter()


@router.get("/recommendations", response_model=RecommendationsResponse)
def read_recommendations(
    creator_id: str,
    session: Session = Depends(get_db_session),
) -> RecommendationsResponse:
    """Return honest, deterministic next-move recommendations from persisted content."""
    if not creator_id or not creator_id.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="creator_id is required")
    return get_recommendations(session, creator_id)
