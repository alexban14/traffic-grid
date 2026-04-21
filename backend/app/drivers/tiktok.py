import random
import logging
import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Page
from playwright_stealth import Stealth
from app.drivers.base import PlatformDriver
from app.models.identity import Identity, Proxy
from app.services.behavioral_dna import BehavioralDNA

logger = logging.getLogger(__name__)

# TikTok cookie consent / popup selectors (they change frequently)
COOKIE_ACCEPT_SELECTORS = [
    'button:has-text("Accept all")',
    'button:has-text("Accept All")',
    'button:has-text("Accepter tout")',
    '[data-testid="cookie-banner-accept"]',
    'button:has-text("Allow all cookies")',
]

LOGIN_DISMISS_SELECTORS = [
    '[data-e2e="modal-close-inner-button"]',
    'button[aria-label="Close"]',
    '.login-modal button.close',
]


class TikTokBrowserDriver(PlatformDriver):
    platform = "tiktok"

    async def _dismiss_popups(self, page: Page):
        """Dismiss cookie consent and login prompts that block video playback."""
        for selector in COOKIE_ACCEPT_SELECTORS:
            try:
                btn = page.locator(selector).first
                if await btn.is_visible(timeout=1000):
                    await btn.click()
                    await self.log("Dismissed cookie consent popup")
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                    break
            except Exception:
                continue

        await asyncio.sleep(random.uniform(1, 2))

        for selector in LOGIN_DISMISS_SELECTORS:
            try:
                btn = page.locator(selector).first
                if await btn.is_visible(timeout=1000):
                    await btn.click()
                    await self.log("Dismissed login popup")
                    await asyncio.sleep(random.uniform(0.5, 1.0))
                    break
            except Exception:
                continue

    async def _wait_for_video_playback(self, page: Page, timeout: int = 15) -> bool:
        """Wait for the TikTok video element to start playing."""
        try:
            # Wait for video element to exist
            await page.wait_for_selector("video", timeout=timeout * 1000)

            # Check if the video is playing (not paused, has currentTime > 0)
            is_playing = await page.evaluate("""
                () => {
                    const video = document.querySelector('video');
                    if (!video) return false;
                    return !video.paused && video.readyState >= 2;
                }
            """)

            if is_playing:
                await self.log("Video playback confirmed (already playing)")
                return True

            # If not playing yet, try clicking the video to trigger play
            try:
                video = page.locator("video").first
                await video.click(timeout=3000)
                await asyncio.sleep(1)
            except Exception:
                pass

            # Poll for playback start
            for _ in range(timeout):
                is_playing = await page.evaluate("""
                    () => {
                        const video = document.querySelector('video');
                        if (!video) return false;
                        return !video.paused && video.currentTime > 0;
                    }
                """)
                if is_playing:
                    await self.log("Video playback confirmed (started after interaction)")
                    return True
                await asyncio.sleep(1)

            await self.log("Warning: video playback could not be confirmed")
            return False

        except Exception as e:
            await self.log(f"Warning: video detection failed: {e}")
            return False

    async def _get_video_duration(self, page: Page) -> Optional[float]:
        """Get the video duration in seconds."""
        try:
            duration = await page.evaluate("""
                () => {
                    const video = document.querySelector('video');
                    return video ? video.duration : null;
                }
            """)
            return duration if duration and duration > 0 else None
        except Exception:
            return None

    async def _watch_video(self, page: Page):
        """Watch the video for a human-like duration based on actual video length."""
        video_duration = await self._get_video_duration(page)

        if video_duration:
            # Watch 70-110% of the video (sometimes loop slightly, sometimes leave early)
            watch_factor = random.uniform(0.7, 1.1)
            watch_time = min(video_duration * watch_factor, 90)  # cap at 90s
            watch_time = max(watch_time, 5)  # minimum 5s
            await self.log(f"Video duration: {video_duration:.1f}s, watching for {watch_time:.1f}s ({watch_factor:.0%})")
        else:
            # Fallback: random dwell if we can't detect duration
            watch_time = random.randint(10, 45)
            await self.log(f"Video duration unknown, dwelling for {watch_time}s")

        # Watch in small intervals, checking playback periodically
        elapsed = 0
        while elapsed < watch_time:
            chunk = min(random.uniform(3, 8), watch_time - elapsed)
            await asyncio.sleep(chunk)
            elapsed += chunk

            # Occasionally check if video is still playing (TikTok might auto-pause)
            if random.random() < 0.1:
                still_playing = await page.evaluate("""
                    () => {
                        const v = document.querySelector('video');
                        return v ? !v.paused : false;
                    }
                """)
                if not still_playing:
                    await self.log("Video paused, clicking to resume")
                    try:
                        await page.locator("video").first.click(timeout=2000)
                    except Exception:
                        pass

    async def execute_view(self, url: str, identity: Identity, proxy: Optional[Proxy] = None) -> bool:
        async with async_playwright() as p:
            browser_args = [
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
            ]
            if proxy:
                browser_args.append(f"--proxy-server={proxy.protocol}://{proxy.ip_address}:{proxy.port}")

            browser = await p.chromium.launch(headless=True, args=browser_args)
            context = await browser.new_context(
                user_agent=identity.user_agent,
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
                timezone_id="Europe/Bucharest",
            )
            page = await context.new_page()

            stealth = Stealth()
            await stealth.apply_stealth_async(page)

            try:
                await self.log(f"Navigating to {url}...")
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)

                # Handle popups before anything else
                await self._dismiss_popups(page)

                # Wait for and verify video playback
                playback_ok = await self._wait_for_video_playback(page)
                if not playback_ok:
                    await self.log("Proceeding despite playback uncertainty")

                # Watch the video (duration-aware)
                await self._watch_video(page)

                # Behavioral scroll (slight, natural movement while watching)
                await BehavioralDNA.human_scroll(page)

                # Random interaction (like, comment check, etc.)
                await BehavioralDNA.curiosity_action(page)

                await self.log("View completed successfully.")
                return True
            except Exception as e:
                logger.error(f"[{self.worker_id}] TikTok view failed: {e}")
                await self.log(f"View failed: {e}")
                return False
            finally:
                await browser.close()

    async def execute_warmup(self, identity: Identity, duration_mins: int) -> bool:
        logger.info(f"[{self.worker_id}] TikTok warmup not yet implemented")
        return False
