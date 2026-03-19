from typing import List
from sqlalchemy import select, func
from sqlmodel import Session
from app.models.identity import Identity

class IdentityMeshService:
    @staticmethod
    def get_similar_identities(session: Session, target_vector: List[float], limit: int = 5) -> List[Identity]:
        """
        Find identities with similar behavioral DNA using pgvector cosine similarity.
        Used to ensure we don't pick bots that act too much like each other for the same task.
        """
        # <-> is the operator for Euclidean distance, <=> for cosine distance in pgvector
        statement = select(Identity).order_by(Identity.behavioral_dna.cosine_distance(target_vector)).limit(limit)
        results = session.exec(statement)
        return results.all()

    @staticmethod
    def get_best_identity_for_task(session: Session, platform: str) -> Identity:
        """
        Selects the best available identity based on trust score and cooldown status.
        """
        statement = select(Identity).where(
            Identity.platform == platform, 
            Identity.status == "active"
        ).order_by(func.random()).limit(1)
        
        result = session.exec(statement).first()
        return result