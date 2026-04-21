# 08 — Task Execution Pipeline

**Last Updated:** 2026-04-21

---

## Overview

TrafficGrid uses a distributed task execution model where tasks flow through a pipeline: **Dispatch → Queue → Execute → Report**. The key entities are:

- **Tasks** — units of work (e.g., "view this TikTok video")
- **Workers** — machines that execute tasks (Docker containers, LXC containers, physical phones)
- **Identities** — fake user profiles workers impersonate (user agent, screen resolution, behavioral DNA)
- **Proxies** — IP addresses workers route traffic through

These are independent pools. No entity is permanently assigned to another — they're bound dynamically at execution time.

---

## Entity Relationships

```
                    ┌──────────────────┐
                    │   Dispatch API   │
                    │  POST /dispatch  │
                    └────────┬─────────┘
                             │ creates Task in DB
                             │ sends to Celery queue
                             ▼
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Identities │     │   Celery/Redis   │     │     Proxies      │
│  (pool of   │◄────│   Task Queue     │────►│  (pool of IPs)   │
│  disguises) │     └────────┬─────────┘     └──────────────────┘
└─────────────┘              │
                    picked up by next
                    available worker
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ Worker 1 │  │ Worker 2 │  │ Worker N │
        │ (Docker) │  │ (LXC)   │  │ (LXC)   │
        └──────────┘  └──────────┘  └──────────┘
```

---

## Current Pipeline (Reactive Identity Assignment)

### Single Video View (`tiktok_views`)

```
1. User dispatches:  POST /dispatch {task_type: "tiktok_views", target_url: "...", volume: 1}
2. Backend creates:  Task record in PostgreSQL (status: PENDING)
3. Backend queues:   Celery task → Redis (status: QUEUED)
4. Worker picks up:  Next available worker takes the task from the queue
5. Worker requests:  IdentityMeshService.get_best_identity_for_task()
                     → returns best available identity (not on cooldown, closest vector)
6. Worker requests:  ProxyManager.get_best_proxy()
                     → returns least-recently-used active proxy (or None)
7. Worker executes:  PlatformDriver.execute_view(url, identity, proxy)
                     → launches stealth Playwright browser
                     → navigates to URL, verifies video playback
                     → watches for duration-aware time
                     → performs random interactions
8. Worker reports:   Updates Task in DB (status: SUCCESS/FAILED, duration, error)
9. Identity cooldown: identity.last_used_at set → 2-hour cooldown starts
```

### Profile Boost (`tiktok_profile_boost`)

```
1. User dispatches:  POST /dispatch {task_type: "tiktok_profile_boost", target_url: "@user", volume: 2}
2. Backend creates:  Parent Task record (status: PENDING)
3. Backend queues:   Celery profile_boost task → Redis
4. Worker picks up:  Scrapes profile page with stealth browser
5. Worker extracts:  Video URLs from profile grid (up to 20)
6. Worker fans out:  For each video × volume:
                       → creates child Task in DB
                       → sends child to Celery queue as tiktok_views task
7. Parent completes: status: SUCCESS, result: {videos_found, tasks_created, child_task_ids}
8. Child tasks:      Picked up by available workers → same flow as single video view
```

---

## Scaling Dimensions

| Dimension | What it controls | Current | Scale target |
|-----------|-----------------|---------|-------------|
| **Workers** | Parallel task execution speed | 2 (1 Docker + 1 LXC) | 10-50 LXC containers |
| **Identities** | Views without cooldown collisions | 20 TikTok + 10 YouTube | 100+ per platform |
| **Proxies** | Unique IP addresses per view | 0 active (placeholder) | 5-20 mobile/residential |
| **Volume** | Views per video | 1 | 10-100 per video |

### Bottleneck Analysis

- **volume=1, 5 videos, 2 workers**: 5 tasks, 2 processed in parallel → ~3 rounds → ~3 min
- **volume=5, 5 videos, 2 workers**: 25 tasks, 2 in parallel → ~13 rounds → ~13 min
- **volume=5, 5 videos, 10 workers**: 25 tasks, 10 in parallel → ~3 rounds → ~3 min
- **Identity constraint**: 20 identities with 2-hour cooldown = max 20 unique views per 2-hour window

---

## Planned: Round-Robin Identity Pre-Assignment

The current reactive assignment has a weakness: when many tasks execute simultaneously, multiple workers may grab the same identity before cooldown is recorded, or all tasks fail because the pool is exhausted.

**Planned improvement:**

```
Profile boost dispatches 50 tasks (10 videos × 5 views each)
→ orchestrator pre-assigns identities round-robin:
    task 1  → identity A
    task 2  → identity B
    ...
    task 20 → identity T
    task 21 → identity A (cooldown expired by now if tasks are spaced)
→ each task carries identity_id — worker doesn't search, just uses it
→ no collisions, no cooldown races, deterministic distribution
```

This also enables: "use each identity exactly once per video" or "spread 100 views across 20 identities = 5 views each, time-delayed."

---

## Task Types Reference

| Task Type | Celery Task Name | Driver | Description |
|-----------|-----------------|--------|-------------|
| `tiktok_views` | `app.tasks.browser.view_boost` | TikTokBrowserDriver | Single video view with playback verification |
| `tiktok_profile_boost` | `app.tasks.browser.profile_boost` | TikTokBrowserDriver | Scrape profile → fan out view tasks |
| `tiktok_warmup` | `app.tasks.mobile.warmup` | TikTokBrowserDriver | Account warm-up (stub) |
| `yt_watchtime` | `app.tasks.browser.view_boost` | YouTubeBrowserDriver | YouTube watch time (stub) |

---

## Database State Machine

```
Task lifecycle:

  PENDING → QUEUED → RUNNING → SUCCESS
                           └→ FAILED

  PENDING:   Created in DB, not yet sent to Celery
  QUEUED:    Sent to Celery, waiting for worker
  RUNNING:   Worker picked it up, executing
  SUCCESS:   Completed successfully, result stored
  FAILED:    Error occurred, error_message stored
```
