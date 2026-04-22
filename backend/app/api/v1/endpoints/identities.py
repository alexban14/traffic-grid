from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.db.session import get_db
from app.models.identity import Identity
from app.models.user import User
from app.core.deps import get_current_user
from app.services.behavioral_dna import BehavioralDNA
from app.services.identity_mesh import IdentityMeshService
from app.schemas.identity import IdentityRegisterRequest, IdentityResponse, BestMatchRequest

router = APIRouter()


@router.post("/register", response_model=IdentityResponse)
async def register_identity(body: IdentityRegisterRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dna_vector = BehavioralDNA.generate_behavior_vector()

    new_identity = Identity(
        username=body.username,
        platform=body.platform,
        status="active",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        behavioral_dna=dna_vector,
    )

    db.add(new_identity)
    db.commit()
    db.refresh(new_identity)

    return IdentityResponse(
        id=new_identity.id,
        username=new_identity.username,
        platform=new_identity.platform,
        status=new_identity.status,
        trust_score=new_identity.trust_score,
    )


@router.post("/best-match", response_model=IdentityResponse)
async def get_best_identity(body: BestMatchRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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

    return IdentityResponse(
        id=identity.id,
        username=identity.username,
        platform=identity.platform,
        status=identity.status,
        trust_score=identity.trust_score,
    )


@router.get("/", response_model=List[IdentityResponse])
async def list_identities(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    identities = db.exec(select(Identity)).all()
    return [
        IdentityResponse(
            id=i.id,
            username=i.username,
            platform=i.platform,
            status=i.status,
            trust_score=i.trust_score,
        )
        for i in identities
    ]
