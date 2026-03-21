from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class WorkerBase(SQLModel):
    name: str
    type: str  # 'LXC-Selenium' | 'Physical-S24' | etc.
    status: str = 'IDLE'
    ip_address: str

class Worker(WorkerBase, table=True):
    __tablename__ = 'workers'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
