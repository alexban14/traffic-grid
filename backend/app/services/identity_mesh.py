from typing import List, Optional
from datetime import datetime, timedelta
from sqlmodel import Session
from sqlalchemy import select, and_
from app.models.identity import Identity

COOLDOWN_HOURS = 2


def _unwrap(row) -> Optional[Identity]:
    """SQLAlchemy select() returns Row objects; extract the model."""
    if row is None:
        return None
    if isinstance(row, Identity):
        return row
    try:
        return row[0]
    except (TypeError, IndexError):
        return row


def _build_identity_filters(platform: str, account_type: Optional[str] = None):
    """Build common identity filters for queries."""
    cooldown_cutoff = datetime.utcnow() - timedelta(hours=COOLDOWN_HOURS)
    filters = [
        Identity.platform == platform,
        Identity.status == "active",
        (Identity.last_used_at.is_(None)) | (Identity.last_used_at <= cooldown_cutoff),
    ]

    if account_type and account_type != "any":
        filters.append(Identity.account_type == account_type)

    return filters


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
        account_type: Optional[str] = None,
    ) -> Optional[Identity]:
        """Select the best identity for a task.

        account_type:
            "authenticated" — only logged-in TikTok accounts
            "anonymous"     — only anonymous (FYP cookies)
            "any" or None   — prefer authenticated, fall back to anonymous
        """
        prefer_authenticated = account_type in (None, "any")

        if prefer_authenticated or account_type == "authenticated":
            # Try authenticated first
            filters = _build_identity_filters(platform, "authenticated")
            filters.append(Identity.behavioral_dna.isnot(None))
            statement = (
                select(Identity)
                .where(and_(*filters))
                .order_by(Identity.behavioral_dna.l2_distance(target_vector))
                .limit(1)
            )
            result = _unwrap(session.exec(statement).first())
            if result:
                return result

            # Authenticated fallback without vector
            filters = _build_identity_filters(platform, "authenticated")
            fallback = (
                select(Identity)
                .where(and_(*filters))
                .order_by(Identity.last_used_at.asc().nulls_first())
                .limit(1)
            )
            result = _unwrap(session.exec(fallback).first())
            if result:
                return result

            # If strict authenticated requested, don't fall back
            if account_type == "authenticated":
                return None

        # Try anonymous (or fall back from "any")
        search_type = "anonymous" if account_type == "anonymous" else None
        filters = _build_identity_filters(platform, search_type)
        filters.append(Identity.behavioral_dna.isnot(None))
        statement = (
            select(Identity)
            .where(and_(*filters))
            .order_by(Identity.behavioral_dna.l2_distance(target_vector))
            .limit(1)
        )
        result = _unwrap(session.exec(statement).first())
        if result:
            return result

        # Final fallback: any active identity
        filters = _build_identity_filters(platform, search_type)
        fallback = (
            select(Identity)
            .where(and_(*filters))
            .order_by(Identity.last_used_at.asc().nulls_first())
            .limit(1)
        )
        return _unwrap(session.exec(fallback).first())

    @staticmethod
    def get_available_identities(
        session: Session,
        platform: str,
        account_type: Optional[str] = None,
    ) -> list[Identity]:
        """Fetch all active identities for round-robin assignment."""
        filters = _build_identity_filters(platform, account_type)
        statement = (
            select(Identity)
            .where(and_(*filters))
            .order_by(Identity.last_used_at.asc().nulls_first())
        )
        rows = session.exec(statement).all()
        return [_unwrap(r) for r in rows]

    @staticmethod
    def mark_identity_used(session: Session, identity_id: int) -> None:
        identity = session.get(Identity, identity_id)
        if identity:
            identity.last_used_at = datetime.utcnow()
            session.add(identity)
            session.commit()
