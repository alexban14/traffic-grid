# 02 — System Architecture Overview

---

## High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CONTROL PLANE (Master)                      │
│   EliteMini (FastAPI) · PostgreSQL · Redis · Celery Beat            │
└──────────────────────────┬───────────────────────┬──────────────────┘
                           │                       │
              ┌────────────┘                       └────────────┐
              ▼                                                 ▼
┌───────────────────────────┐                     ┌───────────────────────────┐
│      WORKER PLANE         │                     │      PROXY GATEWAY        │
│   HP Z420 (Proxmox)       │                     │   MeLe Quieter3Q          │
│                           │                     │                           │
│  ┌─────────────────────┐  │                     │  ┌─────────────────────┐  │
│  │ Selenium LXC #1     │  │◀────────────────────│  │ Mobile Proxy Mesh   │  │
│  └─────────────────────┘  │       Proxy         │  └─────────────────────┘  │
│  ┌─────────────────────┐  │       Traffic       │  ┌─────────────────────┐  │
│  │ Selenium LXC #N     │  │◀────────────────────│  │ Residential Rotation│  │
│  └─────────────────────┘  │                     │  └─────────────────────┘  │
└───────────────────────────┘                     └───────────────────────────┘
              ▲
              │ Task Instructions
              │ (Redis/Celery)
              ▼
┌───────────────────────────┐
│      PHYSICAL PLANE       │
│   Mobile Device Farm      │
│   (S24 Ultra · ADB)       │
└───────────────────────────┘
```

---

## Service Boundaries

| Service | Runtime | Responsibility | Inbound | Outbound |
|---------|---------|---------------|---------|----------|
| **Control API** | FastAPI | Orchestration, dashboard backend, task validation. | HTTP from Dashboard | Redis, PostgreSQL |
| **Task Scheduler**| Celery Beat | Periodic tasks (proxy rotation, heartbeat checks). | N/A | Redis (Task Queue) |
| **Virtual Workers**| Python/Selenium| Executes web-based tasks inside LXC. | Redis Queue | Target Platforms (via Proxy) |
| **Physical Workers**| Python/Appium | Executes mobile-based tasks on devices. | Redis Queue | Target Platforms (via Proxy) |
| **Proxy Gateway** | Proxidize/Python| IP rotation, proxy health monitoring. | HTTP from Workers | Global IP Mesh |

---

## Communication Patterns

### Task Execution Flow

1. **Scheduling**: Control Plane receives a request for 10k TikTok views.
2. **Dispatch**: Celery Beat chunks the request into 500 tasks and pushes to Redis.
3. **Execution**: HP Z420 Workers (Selenium) pick up tasks.
4. **Networking**: Each Worker requests a fresh SOCKS5 proxy from the MeLe Gateway.
5. **Automation**: Selenium performs "undetected" login/navigation on TikTok.
6. **Reporting**: Worker pushes task completion and watch-time metrics back to PostgreSQL.

---

## Hardware Role Mapping

| Hardware | Role | Capacity Target |
|----------|------|-----------------|
| **EliteMini** | Control Plane | Management of 1,000+ concurrent workers. |
| **HP Z420** | Worker Plane | 50-100 concurrent Selenium instances per Xeon node. |
| **MeLe Q3Q** | Proxy Gateway | Routing 500+ Mbps of obfuscated traffic. |
| **S24 Ultra** | Physical Seed | High-authority account actions (Posting, commenting). |
