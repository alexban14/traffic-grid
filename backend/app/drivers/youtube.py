import logging
from typing import Optional
from app.drivers.base import PlatformDriver
from app.models.identity import Identity, Proxy

logger = logging.getLogger(__name__)


class YouTubeBrowserDriver(PlatformDriver):
    platform = "youtube"

    async def execute_view(self, url: str, identity: Identity, proxy: Optional[Proxy] = None) -> bool:
        logger.info(f"[{self.worker_id}] YouTube view driver not yet implemented")
        await self.log("YouTube driver is a stub — not yet implemented.")
        return False

    async def execute_warmup(self, identity: Identity, duration_mins: int) -> bool:
        logger.info(f"[{self.worker_id}] YouTube warmup not yet implemented")
        return False
