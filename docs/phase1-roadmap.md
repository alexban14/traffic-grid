# TrafficGrid — Phase 1 Roadmap (0-100k Views)

**Created:** 2026-04-10
**Last Updated:** 2026-04-21
**Target:** First end-to-end TikTok view through the full pipeline
**Control Plane:** Minisforum UM680 (10.20.20.200 / VLAN 20)

---

## Infrastructure

- [x] MikroTik RB2011 firmware recovery & RouterOS configuration
- [x] VLAN design (10=MGMT, 20=GRID, 30=TRUSTED)
- [x] TP-Link TL-SG108E 802.1Q VLAN configuration (VLANs 10, 20 + PVIDs)
- [x] UM680 connected to VLAN 20 (Port 2), internet verified (10.20.20.200)
- [x] Proxmox VE running on HP Z420 (gitea-vm, livekit-vm, docker-host)
- [x] HP Z420 moved to TP-Link Port 3 (VLAN 10, 10.10.10.104)
- [x] MikroTik firewall rule: allow UM680 (10.20.20.200) → MGMT VLAN (10.10.10.0/24)
- [x] Cross-VLAN communication verified (UM680 ↔ HP Z420 LXC workers)
- [ ] Move MeLE Quieter3Q from PNI switch to TP-Link Port 4 (VLAN 10) — when proxy gateway setup begins
- [ ] Set TP-Link management IP to 10.10.10.2 (VLAN 10)
- [ ] Configure static DHCP leases on MikroTik for UM680 and Z420

## Control Plane (UM680)

- [x] Docker compose stack running (backend, frontend, db, redis, worker, gateway)
- [x] Database schema with Alembic migrations (auto-run on startup)
- [x] `/api/v1/workers/dispatch` endpoint — creates Task in DB, dispatches to Celery
- [x] Celery task pipeline: dispatch → worker picks up → executes → reports back to DB
- [x] Frontend dashboard loads and displays live stats via Tailscale
- [x] Pydantic schemas for all API endpoints (task, worker, proxy, identity, stats)
- [x] Platform driver abstraction (`PlatformDriver` ABC → `TikTokBrowserDriver`, `YouTubeBrowserDriver`)
- [x] BehavioralDNA engine (Bezier scrolling, variable dwell time, curiosity actions)
- [x] Identity mesh with pgvector similarity search + 2-hour cooldown
- [x] Proxy manager with LRU rotation (ready for real proxies)
- [x] Secure credentials (strong passwords for PostgreSQL + Redis, no defaults)
- [x] Consistent port mapping (184xx prefix: backend=18420, socks=18421, gateway=18422, frontend=18423, db=18424, redis=18425)
- [x] `.gitignore` properly excludes `.env`, `node_modules/`, `database/data/`

## Worker Plane (HP Z420 / Proxmox)

> Proxmox running on VLAN 10 (10.10.10.104) with existing VMs (gitea, livekit, docker-host). LXC containers added for TrafficGrid workers.

- [x] Created LXC container `tg-worker-01` (Debian 12, 10.10.10.106)
- [x] Ansible playbook for automated worker provisioning (`setup-worker.yml`)
- [x] Ansible playbook for code deployment (`deploy-code.yml`)
- [x] Google Chrome + Playwright installed via Ansible
- [x] Celery worker agent running as systemd service (`tg-worker.service`)
- [x] Worker connects to UM680 Redis across VLANs (10.10.10.x → 10.20.20.200:18425)
- [x] Worker receives and executes tasks from the shared Celery queue
- [x] SSH key-based auth for Ansible (ed25519 key: `~/.ssh/keys/proxmox-tg-cts`)
- [ ] Write scaling script to clone N LXC workers from base template
- [ ] DNS resolution fix (set nameserver to 1.1.1.1 permanently in LXC template)

## First End-to-End View (MILESTONE ACHIEVED 2026-04-21)

- [x] Dispatch task from dashboard API → Celery queue → Docker/LXC worker
- [x] Playwright launches headless Chromium with stealth plugin
- [x] TikTok page navigated successfully (https://www.tiktok.com/@tiktok)
- [x] BehavioralDNA simulated: 47s dwell time + "Like" interaction
- [x] Task completed in 66 seconds, status `SUCCESS` recorded in PostgreSQL
- [x] Two workers online simultaneously (Docker container + LXC on HP Z420)

## Proxy Gateway (MeLE Quieter3Q) — Not Started

- [ ] Move MeLE from PNI switch to TP-Link Port 4 (VLAN 10)
- [ ] Deploy gateway container on MeLE (SOCKS5 + rotation API)
- [ ] Connect Huawei E3372 USB dongle via powered hub
- [ ] Test modem IP rotation (toggle data via HiLink API)
- [ ] Wire proxy assignment into browser worker task flow
- [ ] Add fallback logic: retry rotation on failure, flag burned IPs

## Automation Refinement — Next Steps

- [ ] Test with real TikTok video URLs (not profile pages)
- [ ] Validate stealth: check if TikTok detects automation
- [ ] Implement TikTok "For You" feed simulation before target navigation
- [ ] Implement YouTube watch time driver
- [ ] Scale test: 10 concurrent workers generating views
- [ ] Trust score tracking: warm-up → cool-down cycle
- [ ] Task scheduling: drip-feed views over time windows

---

## Parking Lot (Phase 2+)

- Authentication & access control on all endpoints
- Instagram/Facebook automation drivers
- Physical device farm (ADB/Appium on S24 Ultra, A40, Moto G40, P10)
- Residential proxy provider API integration (burst capacity)
- Task history, analytics, and performance dashboards
- Romanian market localization (SIM cards, timezone, language)
- CI/CD pipeline and automated testing
- Add spare PCs (HP ProDesk 600 G3 MT, ThinkCentre M92p, ProDesk 600 G3 SFF) as Proxmox cluster nodes
- Multi-node worker scaling
