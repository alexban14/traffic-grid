import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def run_worker(identity_id: int, proxy_url: str):
    async with async_playwright() as p:
        # Launch browser with the MeLe SOCKS5 Proxy
        browser = await p.chromium.launch(
            headless=True,
            proxy={"server": proxy_url}
        )
        
        # Create a unique context (Fingerprint)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 390, 'height': 844}, # iPhone 12/13 size
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True
        )

        page = await context.new_page()
        
        # Apply Stealth to bypass detection
        await stealth_async(page)

        # Navigate to TikTok / YouTube
        print(f"Worker {identity_id}: Navigating to TikTok...")
        await page.goto("https://www.tiktok.com/foryou")
        
from app.services.behavioral_dna import BehavioralDNA

async def run_worker(identity_id: int, proxy_url: str):
    async with async_playwright() as p:
        # ... (setup code remains same) ...
        
        # Apply Stealth
        await stealth_async(page)

        # Navigate to TikTok / YouTube
        print(f"Worker {identity_id}: Navigating to TikTok...")
        await page.goto("https://www.tiktok.com/foryou")
        
        # Advanced Behavioral Logic (DNA)
        for _ in range(10):
            await BehavioralDNA.human_scroll(page)
            await BehavioralDNA.dwell_on_content()
            await BehavioralDNA.curiosity_action(page)

        await browser.close()

if __name__ == "__main__":
    # Example: Connect to MeLe Proxy
    MELE_IP = "192.168.1.50" 
    asyncio.run(run_worker(identity_id=1, proxy_url=f"socks5://{MELE_IP}:1080"))