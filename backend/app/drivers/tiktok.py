import random
import logging
import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Page, BrowserContext
from playwright_stealth import Stealth
from app.drivers.base import PlatformDriver
from app.models.identity import Identity, Proxy
from app.services.behavioral_dna import BehavioralDNA
from app.services.profile_manager import ProfileManager

logger = logging.getLogger(__name__)

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

TIKTOK_FYP_URL = "https://www.tiktok.com/foryou"


class TikTokBrowserDriver(PlatformDriver):
    platform = "tiktok"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile_mgr = ProfileManager()

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

    async def _create_context(self, browser, identity: Identity, proxy: Optional[Proxy] = None) -> BrowserContext:
        """Create a browser context, loading saved profile if available."""
        context_opts = {
            "user_agent": identity.user_agent,
            "viewport": {"width": 1920, "height": 1080},
            "locale": "en-US",
            "timezone_id": "Europe/Bucharest",
        }

        # Load saved session state if profile exists
        state_path = self.profile_mgr.get_storage_state_path("tiktok", identity.username)
        if state_path:
            context_opts["storage_state"] = state_path
            await self.log(f"Loaded saved profile for {identity.username}")
        else:
            await self.log(f"No saved profile for {identity.username} (fresh session)")

        return await browser.new_context(**context_opts)

    async def _save_profile(self, context: BrowserContext, identity: Identity):
        """Save browser session state to disk."""
        try:
            await self.profile_mgr.save_context_state(context, "tiktok", identity.username)
            await self.log(f"Saved profile for {identity.username}")
        except Exception as e:
            logger.warning(f"Failed to save profile for {identity.username}: {e}")

    async def _browse_fyp(self, page: Page, num_videos: int = 2, min_watch: int = 8, max_watch: int = 25):
        """Browse the For You page, watching a few random videos to build session trust."""
        try:
            await self.log(f"Browsing FYP ({num_videos} videos)...")
            await page.goto(TIKTOK_FYP_URL, wait_until="domcontentloaded", timeout=30000)
            await self._dismiss_popups(page)
            await asyncio.sleep(random.uniform(2, 4))

            for i in range(num_videos):
                # Wait for video to load
                playback_ok = await self._wait_for_video_playback(page, timeout=10)
                if playback_ok:
                    watch_time = random.randint(min_watch, max_watch)
                    await self.log(f"  FYP video {i + 1}/{num_videos}: watching {watch_time}s")
                    await asyncio.sleep(watch_time)

                    # Occasional like on FYP (low probability — builds natural pattern)
                    if random.random() < 0.1:
                        try:
                            like_btn = page.locator('[data-e2e="like-icon"]').first
                            if await like_btn.is_visible(timeout=1000):
                                await like_btn.click()
                                await self.log(f"  FYP: liked video {i + 1}")
                                await asyncio.sleep(random.uniform(0.5, 1.5))
                        except Exception:
                            pass

                # Scroll to next video (swipe up)
                if i < num_videos - 1:
                    await page.mouse.wheel(0, random.randint(400, 700))
                    await asyncio.sleep(random.uniform(1.5, 3))

            await self.log("FYP browse complete")
        except Exception as e:
            await self.log(f"FYP browse error (non-critical): {e}")

    async def _wait_for_video_playback(self, page: Page, timeout: int = 15) -> bool:
        """Wait for the TikTok video element to start playing."""
        try:
            await page.wait_for_selector("video", timeout=timeout * 1000)

            is_playing = await page.evaluate("""
                () => {
                    const video = document.querySelector('video');
                    if (!video) return false;
                    return !video.paused && video.readyState >= 2;
                }
            """)

            if is_playing:
                return True

            try:
                video = page.locator("video").first
                await video.click(timeout=3000)
                await asyncio.sleep(1)
            except Exception:
                pass

            for _ in range(timeout):
                is_playing = await page.evaluate("""
                    () => {
                        const video = document.querySelector('video');
                        if (!video) return false;
                        return !video.paused && video.currentTime > 0;
                    }
                """)
                if is_playing:
                    return True
                await asyncio.sleep(1)

            return False
        except Exception:
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
            watch_factor = random.uniform(0.7, 1.1)
            watch_time = min(video_duration * watch_factor, 90)
            watch_time = max(watch_time, 5)
            await self.log(f"Video duration: {video_duration:.1f}s, watching for {watch_time:.1f}s ({watch_factor:.0%})")
        else:
            watch_time = random.randint(10, 45)
            await self.log(f"Video duration unknown, dwelling for {watch_time}s")

        elapsed = 0
        while elapsed < watch_time:
            chunk = min(random.uniform(3, 8), watch_time - elapsed)
            await asyncio.sleep(chunk)
            elapsed += chunk

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
            context = await self._create_context(browser, identity, proxy)
            page = await context.new_page()

            stealth = Stealth()
            await stealth.apply_stealth_async(page)

            try:
                has_profile = self.profile_mgr.has_profile("tiktok", identity.username)

                # Browse FYP first to build/refresh session
                if not has_profile:
                    # First time: longer FYP browse to establish cookies
                    await self._browse_fyp(page, num_videos=3, min_watch=10, max_watch=30)
                else:
                    # Returning: quick FYP refresh
                    await self._browse_fyp(page, num_videos=1, min_watch=5, max_watch=15)

                # Navigate to target video
                await self.log(f"Navigating to {url}...")
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await self._dismiss_popups(page)

                playback_ok = await self._wait_for_video_playback(page)
                if not playback_ok:
                    await self.log("Proceeding despite playback uncertainty")

                await self._watch_video(page)
                await BehavioralDNA.human_scroll(page)
                await BehavioralDNA.curiosity_action(page)

                # Save profile after successful view
                await self._save_profile(context, identity)

                await self.log("View completed successfully.")
                return True
            except Exception as e:
                logger.error(f"[{self.worker_id}] TikTok view failed: {e}")
                await self.log(f"View failed: {e}")
                return False
            finally:
                await browser.close()

    async def execute_warmup(self, identity: Identity, duration_mins: int = 3) -> bool:
        """Browse TikTok FYP to build session cookies and trust for an identity."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = await self._create_context(browser, identity)
            page = await context.new_page()

            stealth = Stealth()
            await stealth.apply_stealth_async(page)

            try:
                # Calculate videos to watch based on duration
                videos_to_watch = max(3, duration_mins * 2)
                await self.log(f"Warming up {identity.username} for ~{duration_mins} min ({videos_to_watch} videos)")

                await self._browse_fyp(page, num_videos=videos_to_watch, min_watch=10, max_watch=30)

                # Save the warmed-up profile
                await self._save_profile(context, identity)

                await self.log(f"Warmup complete for {identity.username}")
                return True
            except Exception as e:
                logger.error(f"[{self.worker_id}] Warmup failed for {identity.username}: {e}")
                await self.log(f"Warmup failed: {e}")
                return False
            finally:
                await browser.close()

    async def scrape_profile_videos(self, profile_url: str, max_videos: int = 20) -> list[str]:
        """Navigate to a TikTok profile and extract video URLs."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
            )
            page = await context.new_page()
            stealth = Stealth()
            await stealth.apply_stealth_async(page)

            try:
                await self.log(f"Scraping profile: {profile_url}")
                await page.goto(profile_url, wait_until="domcontentloaded", timeout=30000)
                await self._dismiss_popups(page)

                await asyncio.sleep(random.uniform(3, 5))

                for _ in range(3):
                    await page.mouse.wheel(0, random.randint(500, 1000))
                    await asyncio.sleep(random.uniform(1.5, 3))

                video_urls = await page.evaluate("""
                    () => {
                        const links = document.querySelectorAll('a[href*="/video/"]');
                        const urls = new Set();
                        links.forEach(link => {
                            const href = link.getAttribute('href');
                            if (href && href.includes('/video/')) {
                                const url = href.startsWith('http') ? href : 'https://www.tiktok.com' + href;
                                urls.add(url);
                            }
                        });
                        return Array.from(urls);
                    }
                """)

                video_urls = video_urls[:max_videos]
                await self.log(f"Found {len(video_urls)} videos on profile")
                return video_urls

            except Exception as e:
                logger.error(f"[{self.worker_id}] Profile scrape failed: {e}")
                await self.log(f"Profile scrape failed: {e}")
                return []
            finally:
                await browser.close()
