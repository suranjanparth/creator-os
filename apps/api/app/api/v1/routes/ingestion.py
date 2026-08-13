from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.domains.ingestion.service import import_creator
from app.schemas.ingestion import CreatorImportRequest, CreatorImportResponse

router = APIRouter()


@router.post("/ingestion/import", response_model=CreatorImportResponse)
def import_creator_payload(
    request: CreatorImportRequest,
    session: Session = Depends(get_db_session),
) -> CreatorImportResponse:
    """Persist an authorized creator's profile and published content idempotently."""
    return import_creator(session, request)
