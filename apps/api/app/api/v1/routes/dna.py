from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.domains.dna.service import get_creator_dna
from app.schemas.dna import DnaResponse

router = APIRouter()


@router.get("/creator-dna", response_model=DnaResponse)
def read_creator_dna(
    creator_id: str,
    session: Session = Depends(get_db_session),
) -> DnaResponse:
    """Return honest, deterministic creative signals derived from persisted content."""
    if not creator_id or not creator_id.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="creator_id is required")
    return get_creator_dna(session, creator_id)
