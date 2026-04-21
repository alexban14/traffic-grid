# 03 — Distributed Worker Plane

---

## Strategy: Hybrid Virtual & Physical Execution

### Virtualization (HP Z420)

To achieve 1M+ views cost-effectively, we utilize high-density virtualization on the HP Z420.

| Aspect | Implementation | Benefit |
|--------|----------------|---------|
| **Host OS** | Proxmox VE | Robust management of containers and VMs. |
| **Container Type** | LXC (Alpine/Ubuntu) | Minimal overhead compared to full VMs; fast startup. |
| **Scaling** | Horizontal per node | Adding more HP Z420 nodes directly increases task capacity. |
| **Isolation** | Unique Browser Profile | Each LXC maintains its own Chrome profile/cookies to prevent cross-account linking. |

### Physical Device Integration (Mobile Farm)

When platforms trigger "Bot Detected" on virtual workers, the system automatically shifts high-value tasks to physical hardware.

- **ADB (Android Debug Bridge)**: Wireless/Wired control of the S24 Ultra and GoPro (for content capture).
- **Appium**: Automating the native TikTok/YouTube apps instead of the web browser.
- **Physical Interaction**: Using system-level commands to simulate real touch events (taps, swipes).

---

## Worker Configuration (LXC)

Each Selenium Worker LXC is provisioned with:
- **CPU**: 1 Core (Xeon E5-1620)
- **RAM**: 512MB - 1GB
- **Disk**: 10GB (Thin Provisioned)
- **Environment**:
  - `undetected-chromedriver` installed.
  - Python 3.12 with `traffic-grid-worker` package.
  - Xvfb (Virtual Framebuffer) for headless browser execution.

---

## Task Priority Matrix

| Task Type | Plane | Reason |
|-----------|-------|--------|
| **Video Views (Low Retention)** | LXC / Selenium | Volume-focused, low trust required. |
| **Video Views (High Retention)**| LXC / Selenium | Sophisticated behavioral modeling needed. |
| **Likes / Shares** | Physical (Appium) | Platform-level trust requirement for engagement metrics. |
| **Account Creation** | Physical (Appium) | Highest detection risk; requires mobile device fingerprint. |
| **Premium Commenting** | Physical (Appium) | Manual/AI-generated high-trust actions. |
