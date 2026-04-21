import random
import asyncio
import logging
import math
from typing import List, Tuple

logger = logging.getLogger(__name__)


class BehavioralDNA:
    """Advanced Humanization Logic for Playwright/ADB Workers."""

    @staticmethod
    async def human_scroll(page):
        """Performs a non-linear, jittery scroll mimicking a human thumb."""
        steps = random.randint(3, 8)
        total_pixels = random.randint(100, 400)

        for i in range(steps):
            progress = i / steps
            prev_progress = (i - 1) / steps if i > 0 else 0
            step_pixels = int(total_pixels * (math.sin(progress * math.pi / 2) - math.sin(prev_progress * math.pi / 2)))
            jitter_x = random.randint(-3, 3)

            await page.mouse.wheel(jitter_x, step_pixels)
            await asyncio.sleep(random.uniform(0.05, 0.15))

    @staticmethod
    async def dwell_on_content(duration_range: Tuple[int, int] = (10, 45)):
        """Simulates a human watching a video with weighted distribution."""
        if random.random() < 0.2:
            duration = random.randint(duration_range[1] // 2, duration_range[1])
        else:
            duration = random.randint(duration_range[0], duration_range[1] // 2)

        logger.info(f"Dwell time: {duration}s")
        await asyncio.sleep(duration)

    @staticmethod
    async def curiosity_action(page):
        """Randomly performs low-stakes interactions on TikTok."""
        actions = ["none", "check_comments", "like", "pause_unpause"]
        weights = [0.55, 0.20, 0.15, 0.10]

        choice = random.choices(actions, weights=weights)[0]

        if choice == "check_comments":
            logger.info("Curiosity: Checking comments...")
            try:
                # TikTok comment button (various selectors)
                for selector in ['[data-e2e="comment-icon"]', 'button[aria-label="Comments"]']:
                    btn = page.locator(selector).first
                    if await btn.is_visible(timeout=2000):
                        await btn.click()
                        await asyncio.sleep(random.uniform(2, 5))
                        # Scroll through a few comments
                        for _ in range(random.randint(1, 3)):
                            await page.mouse.wheel(0, random.randint(100, 200))
                            await asyncio.sleep(random.uniform(0.5, 1.5))
                        # Close comments
                        try:
                            close = page.locator('[data-e2e="browse-close"]').first
                            if await close.is_visible(timeout=1000):
                                await close.click()
                        except Exception:
                            pass
                        break
            except Exception as e:
                logger.debug(f"Comment check failed (non-critical): {e}")

        elif choice == "like":
            logger.info("Interaction: Liking video...")
            try:
                for selector in ['[data-e2e="like-icon"]', 'button[aria-label="Like"]']:
                    btn = page.locator(selector).first
                    if await btn.is_visible(timeout=2000):
                        await btn.click()
                        await asyncio.sleep(random.uniform(0.5, 1.5))
                        break
            except Exception as e:
                logger.debug(f"Like action failed (non-critical): {e}")

        elif choice == "pause_unpause":
            logger.info("Interaction: Pause/unpause video...")
            try:
                video = page.locator("video").first
                if await video.is_visible(timeout=2000):
                    await video.click()  # pause
                    await asyncio.sleep(random.uniform(1, 3))
                    await video.click()  # unpause
            except Exception as e:
                logger.debug(f"Pause/unpause failed (non-critical): {e}")

    @staticmethod
    def generate_behavior_vector() -> List[float]:
        """Generates a 1536-dim dummy vector for the Identity Mesh."""
        return [random.uniform(-1, 1) for _ in range(1536)]
