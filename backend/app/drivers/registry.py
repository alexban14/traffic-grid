from typing import Optional, Callable, Awaitable
from app.drivers.base import PlatformDriver
from app.drivers.tiktok import TikTokBrowserDriver
from app.drivers.youtube import YouTubeBrowserDriver

DRIVER_REGISTRY: dict[str, type[PlatformDriver]] = {
    "tiktok_views": TikTokBrowserDriver,
    "tiktok_profile_boost": TikTokBrowserDriver,
    "tiktok_warmup": TikTokBrowserDriver,
    "yt_watchtime": YouTubeBrowserDriver,
}


def get_driver(
    task_type: str,
    worker_id: str,
    log_callback: Optional[Callable[[str], Awaitable[None]]] = None,
) -> PlatformDriver:
    driver_cls = DRIVER_REGISTRY.get(task_type)
    if not driver_cls:
        raise ValueError(f"No driver registered for task type: {task_type}")
    return driver_cls(worker_id=worker_id, log_callback=log_callback)
