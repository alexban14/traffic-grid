from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, JSON, Column
from datetime import datetime

class TaskBase(SQLModel):
    type: str
    target_url: str
    status: str = 'PENDING'
    config: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

class Task(TaskBase, table=True):
    __tablename__ = 'tasks'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
