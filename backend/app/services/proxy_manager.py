import random
from typing import Optional, List
from sqlmodel import Session, select
from app.models.identity import Proxy
from datetime import datetime

class ProxyManager:
    @staticmethod
    def get_best_proxy(session: Session, provider: Optional[str] = None) -> Optional[Proxy]:
        """
        Selects an active proxy, prioritizing those not used recently.
        """
        statement = select(Proxy).where(Proxy.is_active == True)
        if provider:
            statement = statement.where(Proxy.provider == provider)
        
        statement = statement.order_by(Proxy.last_rotated_at.asc().nulls_first())
        proxy = session.exec(statement).first()
        
        if proxy:
            proxy.last_rotated_at = datetime.utcnow()
            session.add(proxy)
            session.commit()
            
        return proxy

    @staticmethod
    def seed_proxies(session: Session):
        """Seed the initial Digi and Orange proxies."""
        proxies = [
            Proxy(ip_address="192.168.1.100", port=8080, protocol="socks5", provider="Digi RO"),
            Proxy(ip_address="192.168.1.101", port=8080, protocol="socks5", provider="Orange RO"),
        ]
        for p in proxies:
            session.add(p)
        session.commit()
