from typing import List, Optional
from datetime import datetime, timedelta
from sqlmodel import Session
from sqlalchemy import select, and_
from app.models.identity import Identity

COOLDOWN_HOURS = 2


def _unwrap(row) -> Optional[Identity]:
    """SQLAlchemy select() returns Row tuples; extract the model."""
    if row is None:
        return None
    return row[0] if isinstance(row, tuple) else row


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
        return [_unwrap(r) for r in session.exec(statement).all()]

    @staticmethod
    def get_best_identity_for_task(
        session: Session,
        platform: str,
        target_vector: List[float],
    ) -> Optional[Identity]:
        cooldown_cutoff = datetime.utcnow() - timedelta(hours=COOLDOWN_HOURS)

        # Try vector-based matching first
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
        result = _unwrap(session.exec(statement).first())
        if result:
            return result

        # Fallback: any active identity for the platform (no vector required)
        fallback = (
            select(Identity)
            .where(
                and_(
                    Identity.platform == platform,
                    Identity.status == "active",
                    (Identity.last_used_at.is_(None)) | (Identity.last_used_at <= cooldown_cutoff),
                )
            )
            .order_by(Identity.last_used_at.asc().nulls_first())
            .limit(1)
        )
        return _unwrap(session.exec(fallback).first())

    @staticmethod
    def mark_identity_used(session: Session, identity_id: int) -> None:
        identity = session.get(Identity, identity_id)
        if identity:
            identity.last_used_at = datetime.utcnow()
            session.add(identity)
            session.commit()
