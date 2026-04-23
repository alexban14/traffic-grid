import json
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.db.session import get_db
from app.models.identity import Identity
from app.models.user import User
from app.core.deps import get_current_user
from app.services.behavioral_dna import BehavioralDNA
from app.services.identity_mesh import IdentityMeshService
from app.services.profile_manager import ProfileManager
from app.schemas.identity import (
    IdentityRegisterRequest,
    IdentityResponse,
    BestMatchRequest,
    SessionImportRequest,
    SessionHealthResponse,
)

router = APIRouter()
profile_mgr = ProfileManager()


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
        account_type=new_identity.account_type,
        account_status=new_identity.account_status,
    )


@router.post("/best-match", response_model=IdentityResponse)
async def get_best_identity(body: BestMatchRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    target_vector = body.target_vector or BehavioralDNA.generate_behavior_vector()

    identity = IdentityMeshService.get_best_identity_for_task(
        session=db,
        platform=body.platform,
        target_vector=target_vector,
        account_type=body.account_type,
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
        account_type=identity.account_type,
        account_status=identity.account_status,
    )


def _parse_netscape_cookies(text: str) -> list[dict]:
    """Parse Netscape/Mozilla cookie file format into Playwright cookie objects."""
    cookies = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 7:
            continue
        domain, _, path, secure, expires, name, value = parts[:7]
        try:
            exp = float(expires)
        except ValueError:
            exp = -1
        cookies.append({
            "name": name,
            "value": value,
            "domain": domain,
            "path": path,
            "secure": secure.upper() == "TRUE",
            "httpOnly": False,
            "sameSite": "Lax",
            "expires": exp if exp > 0 else -1,
        })
    return cookies


@router.post("/import-session", response_model=IdentityResponse)
async def import_session(body: SessionImportRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Import cookies from a manual browser login to create an authenticated identity.

    cookies_json accepts either:
    - JSON array of cookie objects: [{"name": "...", "value": "...", ...}]
    - Netscape/Mozilla cookie file format (starts with "# Netscape" or has tab-separated lines)
    """
    raw = body.cookies_json.strip()

    # Detect format
    if raw.startswith("["):
        # JSON array
        try:
            cookies = json.loads(raw)
            if not isinstance(cookies, list):
                raise ValueError("Must be a JSON array")
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid cookies JSON: {e}")
    elif "\t" in raw:
        # Netscape format
        cookies = _parse_netscape_cookies(raw)
        if not cookies:
            raise HTTPException(status_code=400, detail="No valid cookies found in Netscape format")
    else:
        raise HTTPException(status_code=400, detail="Unrecognized cookie format. Use JSON array or Netscape format.")

    # Check if identity exists
    existing = db.exec(select(Identity).where(Identity.username == body.username)).first()

    if existing:
        identity = existing
        identity.account_type = "authenticated"
        identity.account_status = "active"
        if body.user_agent:
            identity.user_agent = body.user_agent
    else:
        identity = Identity(
            username=body.username,
            platform=body.platform,
            status="active",
            user_agent=body.user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            account_type="authenticated",
            account_status="active",
            trust_score=80,
            behavioral_dna=BehavioralDNA.generate_behavior_vector(),
        )

    db.add(identity)
    db.commit()
    db.refresh(identity)

    # Save cookies as Playwright storage_state format
    storage_state = {
        "cookies": cookies,
        "origins": [],
    }
    profile_dir = profile_mgr._profile_path(body.platform, body.username)
    profile_dir.mkdir(parents=True, exist_ok=True)
    state_file = profile_mgr._state_file(body.platform, body.username)
    state_file.write_text(json.dumps(storage_state, indent=2))

    # Save metadata
    import datetime
    meta_file = profile_mgr._metadata_file(body.platform, body.username)
    meta_file.write_text(json.dumps({
        "platform": body.platform,
        "username": body.username,
        "account_type": "authenticated",
        "imported_at": datetime.datetime.utcnow().isoformat(),
    }, indent=2))

    return IdentityResponse(
        id=identity.id,
        username=identity.username,
        platform=identity.platform,
        status=identity.status,
        trust_score=identity.trust_score,
        account_type=identity.account_type,
        account_status=identity.account_status,
    )


@router.get("/{identity_id}/health", response_model=SessionHealthResponse)
async def check_identity_health(identity_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Check if an identity has a saved profile and its account status."""
    identity = db.get(Identity, identity_id)
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")

    has_profile = profile_mgr.has_profile(identity.platform, identity.username)

    return SessionHealthResponse(
        identity_id=identity.id,
        username=identity.username,
        has_profile=has_profile,
        account_type=identity.account_type,
        account_status=identity.account_status,
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
            account_type=i.account_type,
            account_status=i.account_status,
        )
        for i in identities
    ]
