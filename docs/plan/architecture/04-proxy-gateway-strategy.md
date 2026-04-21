# Proxy Gateway Strategy: Hybrid Mobile-Residential Mesh

## Decision Summary
To achieve the 1M+ view target on TikTok/YouTube while bypassing modern detection, TrafficGrid will utilize a **Hybrid Proxy Mesh** orchestrated by the MeLe Quieter3Q gateway.

### 1. Tiered Trust Architecture
- **Tier 1: Physical Mobile (USB Dongles)**
  - **Use Case:** Account creation, logins, high-value interactions (comments/likes).
  - **Rationale:** Mobile carrier IPs (CGNAT) are highly trusted and shared with thousands of real users, making them nearly impossible to blacklist without massive collateral damage.
- **Tier 2: Residential Provider (API-based)**
  - **Use Case:** High-volume watch time, background scrolling, mass views.
  - **Rationale:** Scalable on-demand. Used to 'burst' capacity when physical dongles are at max concurrency.

### 2. Hardware: MeLe Quieter3Q Role
- **Host Role:** The MeLe acts as the **Proxy Gateway Controller**.
- **Constraint Management:** Since NullClaw and the Proxy Controller share this hardware, we will use Docker to isolate resources. The fanless design is ideal for 24/7 uptime, but we will monitor CPU thermals during high-concurrency rotation.
- **Networking:** Tailscale will bridge the Proxmox Worker Plane (HP Z420) to the MeLe Gateway.

## Hardware Recommendations: USB Dongles
For the physical mobile tier, we require modems that support **HiLink mode** (for easy API/WebUI control) or **Stick mode** (for direct AT command control via Python).

### Top Picks for TrafficGrid:
1. **Huawei E3372-325 (or -153/607 versions)**
   - **Status:** Industry Standard.
   - **Why:** Massive community support, easily switchable to HiLink, stable for 24/7 use.
   - **Where to buy:** Amazon, AliExpress, or eBay (look for 'unlocked').

2. **ZTE MF833V**
   - **Status:** Modern Alternative.
   - **Why:** Better 4G LTE band support in some regions, works natively with Linux `ModemManager`.
   - **Where to buy:** Amazon, specialized networking stores.

3. **USB Hub (Critical):**
   - **Recommendation:** TP-Link UH700 or a powered Sabrent 7-Port USB 3.0 Hub.
   - **Why:** The MeLe cannot power multiple cellular modems from its onboard ports. A **powered** hub is mandatory to prevent voltage drops and modem disconnects.

## Implementation Roadmap
1. **Orchestrator:** Python-based service on MeLe to manage `ModemManager`.
2. **Rotation:** Scripted IP reset via HTTP API (HiLink) or AT+CFUN (Stick).
3. **Failover:** Logic to route traffic to Residential Provider if local modems report high latency or 'burned' status.