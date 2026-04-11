from pydantic import BaseModel
from typing import Optional, List


class IdentityRegisterRequest(BaseModel):
    username: str
    platform: str


class IdentityResponse(BaseModel):
    id: int
    username: str
    platform: str
    status: str
    trust_score: int


class BestMatchRequest(BaseModel):
    platform: str
    target_vector: Optional[List[float]] = None
