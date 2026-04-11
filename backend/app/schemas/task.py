from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TaskType(str, Enum):
    TIKTOK_VIEWS = "tiktok_views"
    TIKTOK_WARMUP = "tiktok_warmup"
    YT_WATCHTIME = "yt_watchtime"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class DispatchRequest(BaseModel):
    task_type: TaskType
    target_url: str
    volume: int = 1


class DispatchResponse(BaseModel):
    task_id: int
    celery_task_id: str
    status: TaskStatus


class TaskResponse(BaseModel):
    id: int
    type: str
    target_url: str
    status: str
    config: Optional[Dict[str, Any]] = None
    celery_task_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
