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
    account_type: str = "anonymous"
    account_status: str = "active"


class BestMatchRequest(BaseModel):
    platform: str
    target_vector: Optional[List[float]] = None
    account_type: Optional[str] = None


class SessionImportRequest(BaseModel):
    username: str
    platform: str = "tiktok"
    cookies_json: str  # JSON string of cookies array
    user_agent: Optional[str] = None


class SessionHealthResponse(BaseModel):
    identity_id: int
    username: str
    has_profile: bool
    account_type: str
    account_status: str
