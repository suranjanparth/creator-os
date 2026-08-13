from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.domains.dashboard.development_data import DEVELOPMENT_CREATOR_ID
from app.domains.dna.service import get_creator_dna
from app.schemas.dna import DnaResponse

router = APIRouter()


@router.get("/creator-dna", response_model=DnaResponse)
def read_creator_dna(
    creator_id: str = DEVELOPMENT_CREATOR_ID,
    session: Session = Depends(get_db_session),
) -> DnaResponse:
    """Return honest, deterministic creative signals derived from persisted content."""
    return get_creator_dna(session, creator_id)
