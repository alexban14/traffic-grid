from typing import Optional, List
from sqlmodel import SQLModel, Field, Column
from pgvector.sqlalchemy import Vector
from datetime import datetime

class IdentityBase(SQLModel):
    username: str = Field(index=True, unique=True)
    platform: str
    status: str = "warming_up"
    user_agent: str
    screen_resolution: Optional[str] = None

class Identity(IdentityBase, table=True):
    __tablename__ = "identities"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Behavioral DNA Vector (1536 dimensions for Gemini/OpenAI compatibility)
    behavioral_dna: Optional[List[float]] = Field(
        sa_column=Column(Vector(1536))
    )

class ProxyBase(SQLModel):
    ip_address: str
    port: int
    protocol: str = "socks5"
    provider: Optional[str] = None
    is_active: bool = True

class Proxy(ProxyBase, table=True):
    __tablename__ = "proxies"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    last_rotated_at: Optional[datetime] = None