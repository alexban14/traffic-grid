# 01 — Admin Dashboard

## Overview

The TrafficGrid Dashboard is the central command center for orchestrating the bot farm. It provides real-time visibility into worker health, proxy performance, task progress, and account trust scores. Built with React 19 and TanStack, it is designed for high-density information display and low-latency interaction.

---

## Key Modules

### 1. Worker Plane Management
- **Cluster Overview**: CPU/RAM utilization of the HP Z420 Proxmox nodes.
- **Worker Status**: Grid view of all active LXC/Physical workers.
  - Indicators: IDLE, BUSY, ERROR, INITIALIZING.
  - Live Log: Real-time console output from a specific worker.
  - Remote View: VNC/Vite-based view into the worker's browser window.

### 2. Task Orchestration
- **Task Creator**: Wizard to define a new objective.
  - Platform: TikTok, YouTube, IG.
  - Action: Views, Likes, Shares, Comments.
  - Target URL: Video or Channel link.
  - Volume: Total targeted actions.
  - Scheduling: Immediate, Drip-feed, or Peak-hour scheduling.
- **Active Tasks**: Progress bars for all running campaigns.
  - Real-time success/failure rate per campaign.

### 3. Account Profile Center
- **Identity Vault**: Management of stored cookies and browser profiles.
- **Trust Metrics**: A numerical score (0-100) per account based on platform flags.
- **Action History**: Chronological log of what each account has done across platforms.

### 4. Proxy Mesh Dashboard
- **Gateway Health**: Uptime and latency of the MeLe Quieter3Q.
- **IP Rotation Control**: Manual "Hard Reset" button for mobile dongles.
- **Usage Heatmap**: Geographical distribution of currently assigned residential IPs.

---

## User Stories

- **As an Operator**, I want to see which workers are failing so I can troubleshoot Proxmox or Proxy issues.
- **As an Operator**, I want to drip-feed 100k views over 48 hours to avoid TikTok's sudden engagement spike alerts.
- **As an Operator**, I want to switch a task from "LXC Selenium" to "Physical S24 Ultra" if I detect a "Browser Not Supported" error.
- **As an Operator**, I want to view the live browser session of a worker to see if a platform has updated its UI layout.

---

## Acceptance Criteria

- [ ] Dashboard loads in < 1 second using TanStack Query caching.
- [ ] Worker status grid updates via WebSockets (FastAPI integration).
- [ ] Task creation supports Zod-validated JSON payloads.
- [ ] VNC/Remote view integrates seamlessly into the browser UI.
- [ ] Sidebar provides "System Health" indicators for EliteMini, HP Z420, and MeLe nodes.
