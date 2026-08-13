from fastapi import APIRouter

from app.api.v1.routes.analytics import router as analytics_router
from app.api.v1.routes.content import router as content_router
from app.api.v1.routes.content_intelligence import router as content_intelligence_router
from app.api.v1.routes.creators import router as creators_router
from app.api.v1.routes.dashboard import router as dashboard_router
from app.api.v1.routes.dna import router as dna_router
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.ingestion import router as ingestion_router
from app.api.v1.routes.recommendations import router as recommendations_router

api_router = APIRouter()
api_router.include_router(analytics_router, tags=["analytics"])
api_router.include_router(content_router, tags=["content"])
api_router.include_router(content_intelligence_router, tags=["content intelligence"])
api_router.include_router(creators_router, tags=["creators"])
api_router.include_router(dashboard_router, tags=["dashboard"])
api_router.include_router(dna_router, tags=["creator dna"])
api_router.include_router(health_router, tags=["health"])
api_router.include_router(ingestion_router, tags=["ingestion"])
api_router.include_router(recommendations_router, tags=["recommendations"])
