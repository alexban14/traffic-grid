from fastapi import APIRouter

from app.db.session import get_session
from app.models.identity import Identity

from app.services.identity_mesh import IdentityMeshService

router = APIRouter()

@router.get("/recommend")
async def recommend_identity(platform: str, session: Session = Depends(get_session)):
    identity = IdentityMeshService.get_best_identity_for_task(session, platform)
    if not identity:
        raise HTTPException(status_code=404, detail="No suitable identity found")
    return identity

@router.get("/summary")
async def get_identities_summary(session: Session = Depends(get_session)):
    # In a real scenario, we'd query the DB here
    return {"total": 1024, "active": 4, "burned": 12}