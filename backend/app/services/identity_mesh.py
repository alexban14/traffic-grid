from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlmodel import Session
from app.models.identity import Identity

COOLDOWN_HOURS = 2

class IdentityMeshService:
    @staticmethod
    def get_similar_identities(
        session: Session,
        target_vector: List[float],
        limit: int = 5,
        platform: Optional[str] = None,
    ) -> List[Identity]:
        filters = [Identity.behavioral_dna.isnot(None)]
        if platform:
            filters.append(Identity.platform == platform)

        statement = (
            select(Identity)
            .where(and_(*filters))
            .order_by(Identity.behavioral_dna.l2_distance(target_vector))
            .limit(limit)
        )
        return session.exec(statement).all()

    @staticmethod
    def get_best_identity_for_task(
        session: Session,
        platform: str,
        target_vector: List[float],
    ) -> Optional[Identity]:
        cooldown_cutoff = datetime.utcnow() - timedelta(hours=COOLDOWN_HOURS)

        statement = (
            select(Identity)
            .where(
                and_(
                    Identity.platform == platform,
                    Identity.status == "active",
                    Identity.behavioral_dna.isnot(None),
                    (Identity.last_used_at.is_(None)) | (Identity.last_used_at <= cooldown_cutoff),
                )
            )
            .order_by(Identity.behavioral_dna.l2_distance(target_vector))
            .limit(1)
        )
        return session.exec(statement).first()

    @staticmethod
    def mark_identity_used(session: Session, identity_id: int) -> None:
        identity = session.get(Identity, identity_id)
        if identity:
            identity.last_used_at = datetime.utcnow()
            session.add(identity)
            session.commit()
