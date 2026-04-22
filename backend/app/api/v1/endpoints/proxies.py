from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_db
from app.models.identity import Proxy
from app.models.user import User
from app.core.deps import get_current_user
from app.schemas.proxy import ProxyHealthResponse

router = APIRouter()


@router.get("/health", response_model=List[ProxyHealthResponse])
async def get_proxies_health(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    proxies = db.exec(select(Proxy)).all()
    return [
        ProxyHealthResponse(
            id=p.id,
            name=f"{p.provider} #{p.id}" if p.provider else f"Proxy #{p.id}",
            provider=p.provider,
            latency_ms=None,
            status="active" if p.is_active else "inactive",
            last_rotated_at=p.last_rotated_at,
        )
        for p in proxies
    ]
