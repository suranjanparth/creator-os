from app.domains.dashboard.development_data import DEVELOPMENT_CREATOR_ID
from app.schemas.creator import CreatorProfileCreate

DEVELOPMENT_CREATOR_PROFILE = CreatorProfileCreate(
    creator_id=DEVELOPMENT_CREATOR_ID,
    name="Maya Chen",
    handle="@mayamakes",
    niche="Creative systems & solo business",
    platform="Instagram",
    audience="Ambitious creatives, 24-34",
    follower_count=84_200,
)
