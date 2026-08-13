from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.domains.content.ingestion import ingest_content_batch
from app.domains.content.service import get_creator_content, ingest_content
from app.schemas.content import (
    ContentIngestRequest,
    ContentIngestResponse,
    CreatorContentCreate,
    CreatorContentResponse,
)

router = APIRouter()


@router.post("/content", response_model=CreatorContentResponse, status_code=status.HTTP_201_CREATED)
def create_creator_content(content: CreatorContentCreate, session: Session = Depends(get_db_session)) -> CreatorContentResponse:
    try:
        return ingest_content(session, content)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@router.post("/content/ingest", response_model=ContentIngestResponse)
def ingest_creator_content_batch(
    request: ContentIngestRequest,
    session: Session = Depends(get_db_session),
) -> ContentIngestResponse:
    try:
        return ingest_content_batch(session, request)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error


@router.get("/content", response_model=list[CreatorContentResponse])
def read_creator_content(creator_id: str, session: Session = Depends(get_db_session)) -> list[CreatorContentResponse]:
    return get_creator_content(session, creator_id)
