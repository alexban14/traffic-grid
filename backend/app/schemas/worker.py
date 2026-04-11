from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WorkerHeartbeatRequest(BaseModel):
    name: str
    type: str
    ip_address: str


class WorkerHeartbeatResponse(BaseModel):
    status: str
    worker_id: int


class WorkerStatusResponse(BaseModel):
    id: str
    type: str
    status: str
    load: float
    last_seen: Optional[datetime] = None
