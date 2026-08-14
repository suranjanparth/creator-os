from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.domains.dashboard.service import get_dashboard
from app.schemas.dashboard import DashboardResponse

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
def read_dashboard(
    creator_id: str,
    session: Session = Depends(get_db_session),
) -> DashboardResponse:
    """Return a creator-scoped dashboard derived from persisted content."""
    if not creator_id or not creator_id.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="creator_id is required")
    return get_dashboard(session, creator_id)
