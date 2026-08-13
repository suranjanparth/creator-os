from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.domains.dashboard.development_data import DEVELOPMENT_CREATOR_ID
from app.domains.recommendations.service import get_recommendations
from app.schemas.recommendations import RecommendationsResponse

router = APIRouter()


@router.get("/recommendations", response_model=RecommendationsResponse)
def read_recommendations(
    creator_id: str = DEVELOPMENT_CREATOR_ID,
    session: Session = Depends(get_db_session),
) -> RecommendationsResponse:
    """Return honest, deterministic next-move recommendations from persisted content."""
    return get_recommendations(session, creator_id)
