from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def get_proxies_health():
    return [
        {"name": "Orange RO #1", "latency": "182ms", "status": "active"},
        {"name": "Digi RO #1", "latency": "95ms", "status": "active"}
    ]