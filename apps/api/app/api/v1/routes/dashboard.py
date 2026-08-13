from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.domains.dashboard.development_data import DEVELOPMENT_CREATOR_ID
from app.domains.dashboard.service import get_dashboard
from app.schemas.dashboard import DashboardResponse

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
def read_dashboard(
    creator_id: str = DEVELOPMENT_CREATOR_ID,
    session: Session = Depends(get_db_session),
) -> DashboardResponse:
    """Return a creator-scoped dashboard derived from persisted content."""
    return get_dashboard(session, creator_id)
