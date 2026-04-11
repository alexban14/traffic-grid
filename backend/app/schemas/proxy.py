from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProxyHealthResponse(BaseModel):
    id: int
    name: str
    provider: Optional[str] = None
    latency_ms: Optional[int] = None
    status: str
    last_rotated_at: Optional[datetime] = None
