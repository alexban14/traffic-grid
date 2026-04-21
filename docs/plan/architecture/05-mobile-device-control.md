# TrafficGrid: Physical Phone Control Architecture

## 📱 Orchestration Layer
To automate the physical device farm (S24 Ultra, A40, Moto G40, P10), we will use a **Hub-and-Spoke** model.

### 1. The Controller (HP Z420 / Proxmox)
- **ADB Server:** Acts as the central daemon for all USB/Wireless connections.
- **LXC Container:** A dedicated Linux Container (`traffic-grid-mobile`) will run the Python automation scripts.
- **Tools:** 
  - `uiautomator2`: For fast, XML-based UI interaction (clicks, swipes, text entry).
  - `scrcpy`: For visual verification and low-latency screen streaming if we need to manually intervene.
  - `adb-sync`: For pushing content (videos/images) to the devices.

### 2. The Network (Tailscale / Local Hub)
- **Physical Connection:** The devices will be plugged into a **Powered USB Hub** connected to the HP Z420.
- **Wireless ADB:** For the S24 Ultra (if not physically tethered), we will use Wireless ADB over the local network for maximum mobility.

## 🛠️ Interaction Logic
We will build a **Behavioral Wrapper** around `uiautomator2` to avoid "robotic" patterns:
- **Randomized Bezier Swipes:** Mimicking human thumb movement instead of straight-line scrolls.
- **Variable Click Duration:** Holding a "Like" button for 150ms vs 300ms randomly.
- **OCR Integration:** Using `EasyOCR` or `Tesseract` to "read" the screen when standard UI selectors fail (common in TikTok's obfuscated views).

## 🚀 Workflow Example
1. **Brain (MeLe)** sends a gRPC command to **Mobile Worker (Z420)**.
2. **Mobile Worker** selects an available device (e.g., Moto G40).
3. **ADB** wakes the screen and unlocks via PIN.
4. **uiautomator2** opens TikTok and performs the "Warm-up" sequence.
5. **ADB** reports success/failure back to the **Brain**.