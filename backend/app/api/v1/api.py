from fastapi import APIRouter
from app.api.v1.endpoints import workers, proxies, identities, stats

api_router = APIRouter()
api_router.include_router(workers.router, prefix="/workers", tags=["workers"])
api_router.include_router(proxies.router, prefix="/proxies", tags=["proxies"])
api_router.include_router(identities.router, prefix="/identities", tags=["identities"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
