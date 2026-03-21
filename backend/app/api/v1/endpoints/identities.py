from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.identity import Identity
from app.services.behavioral_dna import BehavioralDNA

router = APIRouter()

@router.post("/register", response_model=dict)
async def register_identity(username: str, platform: str, db: Session = Depends(get_db)):
    # Generate initial behavioral DNA vector
    dna_vector = BehavioralDNA.generate_behavior_vector()
    
    new_identity = Identity(
        username=username,
        platform=platform,
        status="active",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        behavioral_dna=dna_vector
    )
    
    db.add(new_identity)
    db.commit()
    db.refresh(new_identity)
    
    return {"status": "registered", "identity_id": new_identity.id, "trust_score": 50}

@router.get("/", response_model=List[dict])
async def list_identities(db: Session = Depends(get_db)):
    identities = db.query(Identity).all()
    return [{"username": i.username, "platform": i.platform, "status": i.status} for i in identities]
