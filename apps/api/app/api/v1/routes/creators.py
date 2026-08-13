from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.domains.creators.repository import get_creator_profile
from app.domains.creators.service import get_creator_profiles, save_creator_profile, serialize_creator_profile
from app.schemas.creator import CreatorProfileCreate, CreatorProfileResponse

router = APIRouter()


@router.get("/creators", response_model=list[CreatorProfileResponse])
def read_creator_profiles(
    session: Session = Depends(get_db_session),
) -> list[CreatorProfileResponse]:
    return get_creator_profiles(session)


@router.post("/creators", response_model=CreatorProfileResponse, status_code=status.HTTP_201_CREATED)
def create_creator_profile(
    profile: CreatorProfileCreate,
    session: Session = Depends(get_db_session),
) -> CreatorProfileResponse:
    try:
        return save_creator_profile(session, profile)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@router.get("/creators/{creator_id}", response_model=CreatorProfileResponse)
def read_creator_profile(
    creator_id: str,
    session: Session = Depends(get_db_session),
) -> CreatorProfileResponse:
    record = get_creator_profile(session, creator_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Creator '{creator_id}' not found")
    return serialize_creator_profile(record)
