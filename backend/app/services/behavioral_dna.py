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
        steps = random.randint(5, 12)
        total_pixels = random.randint(400, 800)

        for i in range(steps):
            progress = i / steps
            step_pixels = int(total_pixels * (math.sin(progress * math.pi / 2) - math.sin((i-1)/steps * math.pi / 2)))
            jitter_x = random.randint(-5, 5)

            await page.mouse.wheel(jitter_x, step_pixels)
            await asyncio.sleep(random.uniform(0.05, 0.2))

    @staticmethod
    async def dwell_on_content(duration_range: Tuple[int, int] = (10, 45)):
        """Simulates a human watching a video."""
        if random.random() < 0.2:
            duration = random.randint(duration_range[1] // 2, duration_range[1])
        else:
            duration = random.randint(duration_range[0], duration_range[1] // 2)

        logger.info(f"Dwell time: {duration}s")
        await asyncio.sleep(duration)

    @staticmethod
    async def curiosity_action(page):
        """Randomly performs low-stakes interactions (e.g., checking comments)."""
        actions = ["none", "check_comments", "like", "pause_unpause"]
        weights = [0.6, 0.2, 0.15, 0.05]

        choice = random.choices(actions, weights=weights)[0]

        if choice == "check_comments":
            logger.info("Curiosity: Checking comments...")
        elif choice == "like":
            logger.info("Interaction: Liking video...")

    @staticmethod
    def generate_behavior_vector() -> List[float]:
        """Generates a 1536-dim dummy vector for the Identity Mesh."""
        return [random.uniform(-1, 1) for _ in range(1536)]
