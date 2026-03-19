import time
import uiautomator2 as u2
from typing import List, Dict

class PhysicalPhoneController:
    def __init__(self, device_serial: str, adb_host: str = "127.0.0.1"):
        self.device_serial = device_serial
        # Connect to a remote ADB server (e.g., on the Z420)
        self.d = u2.connect(f"{adb_host}:5037") 
        print(f"Connected to device {device_serial} via ADB Host {adb_host}")

    def unlock_device(self, pin: str = "0000"):
        """Wakes and unlocks the device."""
        self.d.screen_on()
        time.sleep(1)
        if self.d(resourceId="com.android.systemui:id/lock_icon").exists:
            self.d.swipe(0.5, 0.8, 0.5, 0.2) # Swipe up to unlock
            time.sleep(1)
            for digit in pin:
                self.d(text=digit).click()
            self.d(description="Done").click() # Or enter key

    def open_tiktok(self):
        """Opens TikTok and waits for the feed to load."""
        self.d.app_start("com.zhiliaoapp.musically")
        time.sleep(5)

    def human_scroll(self, loops: int = 10):
        """Performs randomized scrolls to mimic human behavior."""
        for _ in range(loops):
            # Randomized swipe coordinates
            start_x = 0.5 + (time.time() % 0.1 - 0.05)
            start_y = 0.8 + (time.time() % 0.1 - 0.05)
            end_y = 0.2 + (time.time() % 0.1 - 0.05)
            
            self.d.swipe(start_x, start_y, start_x, end_y, duration=0.2)
            
            # Random watch time (7-15 seconds)
            watch_time = 7 + (time.time() % 8)
            time.sleep(watch_time)

if __name__ == "__main__":
    # Example: S24 Ultra Serial
    controller = PhysicalPhoneController("R5CW10XXXXX")
    controller.unlock_device()
    controller.open_tiktok()
    controller.human_scroll(loops=5)