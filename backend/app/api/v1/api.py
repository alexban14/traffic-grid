from fastapi import APIRouter
from app.api.v1.endpoints import workers, proxies, identities

api_router = APIRouter()
api_router.include_router(workers.router, prefix="/workers", tags=["workers"])
api_router.include_router(proxies.router, prefix="/proxies", tags=["proxies"])
api_router.include_router(identities.router, prefix="/identities", tags=["identities"])