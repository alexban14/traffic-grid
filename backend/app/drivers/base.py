from abc import ABC, abstractmethod
from typing import Optional, Callable, Awaitable
from app.models.identity import Identity, Proxy


class PlatformDriver(ABC):
    """Abstract base for all platform execution drivers."""

    platform: str

    def __init__(self, worker_id: str, log_callback: Optional[Callable[[str], Awaitable[None]]] = None):
        self.worker_id = worker_id
        self._log_callback = log_callback

    async def log(self, message: str):
        if self._log_callback:
            await self._log_callback(message)

    @abstractmethod
    async def execute_view(self, url: str, identity: Identity, proxy: Optional[Proxy] = None) -> bool:
        ...

    @abstractmethod
    async def execute_warmup(self, identity: Identity, duration_mins: int) -> bool:
        ...
