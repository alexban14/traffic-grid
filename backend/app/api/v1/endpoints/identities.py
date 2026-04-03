from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List, Optional
from pydantic import BaseModel

from app.db.session import get_db
from app.models.identity import Identity
from app.services.behavioral_dna import BehavioralDNA
from app.services.identity_mesh import IdentityMeshService

router = APIRouter()

class BestIdentityRequest(BaseModel):
    platform: str
    target_vector: Optional[List[float]] = None

@router.post("/register", response_model=dict)
async def register_identity(username: str, platform: str, db: Session = Depends(get_db)):
    dna_vector = BehavioralDNA.generate_behavior_vector()

    new_identity = Identity(
        username=username,
        platform=platform,
        status="active",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        behavioral_dna=dna_vector,
    )

    db.add(new_identity)
    db.commit()
    db.refresh(new_identity)

    return {"status": "registered", "identity_id": new_identity.id, "trust_score": 50}

@router.post("/best-match", response_model=dict)
async def get_best_identity(body: BestIdentityRequest, db: Session = Depends(get_db)):
    target_vector = body.target_vector or BehavioralDNA.generate_behavior_vector()

    identity = IdentityMeshService.get_best_identity_for_task(
        session=db,
        platform=body.platform,
        target_vector=target_vector,
    )
    if not identity:
        raise HTTPException(
            status_code=404,
            detail=f"No available identity for platform {body.platform} (all may be on cooldown)",
        )

    IdentityMeshService.mark_identity_used(db, identity.id)

    return {
        "identity_id": identity.id,
        "username": identity.username,
        "platform": identity.platform,
        "trust_score": identity.trust_score,
    }

@router.get("/", response_model=List[dict])
async def list_identities(db: Session = Depends(get_db)):
    identities = db.query(Identity).all()
    return [
        {"username": i.username, "platform": i.platform, "status": i.status}
        for i in identities
    ]
