from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, JSON, Column
from datetime import datetime


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    type: str
    target_url: str
    status: str = "PENDING"
    config: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    celery_task_id: Optional[str] = None
    worker_id: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
