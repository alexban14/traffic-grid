import asyncio
import random
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from app.services.behavioral_dna import BehavioralDNA
from app.core.websocket import manager

class BrowserWorker:
    def __init__(self, worker_id: str):
        self.worker_id = worker_id

    async def log(self, message: str):
        print(f"[{self.worker_id}] {message}")
        await manager.broadcast_to_worker(message, self.worker_id)

    async def run_view_boost(self, url: str, identity, proxy=None):
        async with async_playwright() as p:
            browser_args = []
            if proxy:
                browser_args.append(f"--proxy-server={proxy.protocol}://{proxy.ip_address}:{proxy.port}")
            
            browser = await p.chromium.launch(headless=True, args=browser_args)
            context = await browser.new_context(user_agent=identity.user_agent)
            page = await context.new_page()
            
            # Apply stealth
            await stealth_async(page)
            
            try:
                await self.log(f"Navigating to {url}...")
                await page.goto(url, wait_until="networkidle")
                
                # Human-like dwell
                await self.log("Simulating human dwell time...")
                await BehavioralDNA.dwell_on_content((15, 60))
                
                # Human-like scroll
                await self.log("Performing behavioral scroll...")
                await BehavioralDNA.human_scroll(page)
                
                # Random interaction
                await self.log("Checking for curiosity actions...")
                await BehavioralDNA.curiosity_action(page)
                
                await self.log("Task completed successfully.")
                return True
            except Exception as e:
                await self.log(f"Task failed: {str(e)}")
                return False
            finally:
                await browser.close()
