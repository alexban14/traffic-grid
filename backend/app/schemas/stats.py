from pydantic import BaseModel
from typing import Optional


class StatsResponse(BaseModel):
    active_workers: int
    total_identities: int
    success_rate: float
    proxy_latency_ms: Optional[int] = None
    tasks_pending: int
    tasks_running: int
