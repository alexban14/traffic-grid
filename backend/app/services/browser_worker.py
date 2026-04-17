import logging
from typing import Optional
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from app.services.behavioral_dna import BehavioralDNA
from app.models.identity import Identity, Proxy

logger = logging.getLogger(__name__)


async def create_browser_context(playwright, identity: Identity, proxy: Optional[Proxy] = None):
    """Shared Playwright browser setup used by all browser-based drivers."""
    browser_args = []
    if proxy:
        browser_args.append(f"--proxy-server={proxy.protocol}://{proxy.ip_address}:{proxy.port}")

    browser = await playwright.chromium.launch(headless=True, args=browser_args)
    context = await browser.new_context(user_agent=identity.user_agent)
    page = await context.new_page()
    stealth = Stealth()
    await stealth.apply_stealth_async(page)

    return browser, context, page
