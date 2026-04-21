# 09 — Orchestration Framework: Technical Architecture

**Last Updated:** 2026-04-21
**Status:** Operational — first e2e pipeline verified

---

## System Overview

TrafficGrid is a distributed task orchestration framework for automated social media engagement. The system follows a **Control Plane / Worker Plane** separation across physically isolated VLAN segments, communicating through a Redis-backed Celery task queue.

```
┌─────────────────────────────── VLAN 20 (10.20.20.0/24) ─────────────────────────────────┐
│                                                                                          │
│  Minisforum UM680 (10.20.20.200) — Control Plane                                        │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐  │
│  │  Docker Compose Stack                                                               │  │
│  │                                                                                     │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │  │
│  │  │ FastAPI   │  │ Celery   │  │ PostgreSQL│  │  Redis   │  │  nginx   │  │Gateway │ │  │
│  │  │ :18420   │  │ Worker   │  │  :18424  │  │  :18425  │  │  :18423  │  │:18421  │ │  │
│  │  │          │  │ (local)  │  │ pgvector │  │  broker  │  │   SPA    │  │SOCKS5  │ │  │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────┘  └────────┘ │  │
│  │       │              │              │              │                                 │  │
│  │       └──────────────┴──────────────┴──────────────┘                                 │  │
│  │                     tg-network (Docker bridge)                                       │  │
│  └─────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                          │
└──────────────────────────────────┬───────────────────────────────────────────────────────┘
                                   │ MikroTik inter-VLAN routing
                                   │ Firewall: allow 10.20.20.200 → 10.10.10.0/24
┌──────────────────────────────────┴───────────────────────────────────────────────────────┐
│                                                                                          │
│  ┌─────────────────── VLAN 10 (10.10.10.0/24) ──────────────────────────┐               │
│  │                                                                       │               │
│  │  HP Z420 / Proxmox (10.10.10.104) — Worker Plane                     │               │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │               │
│  │  │  LXC: tg-worker-01 (10.10.10.106)                              │  │               │
│  │  │  ┌───────────────────────────────────────────────────────────┐  │  │               │
│  │  │  │  systemd: tg-worker.service                               │  │  │               │
│  │  │  │  Celery Worker → redis://10.20.20.200:18425/0             │  │  │               │
│  │  │  │  Queues: browser-queue, mobile-queue, celery              │  │  │               │
│  │  │  │  Concurrency: 2 (prefork)                                 │  │  │               │
│  │  │  │  Runtime: Python 3.12 venv + Playwright + Chrome 147      │  │  │               │
│  │  │  └───────────────────────────────────────────────────────────┘  │  │               │
│  │  └─────────────────────────────────────────────────────────────────┘  │               │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │               │
│  │  │  LXC: tg-worker-02..N (cloned from template)                   │  │               │
│  │  │  (planned — scaling script not yet implemented)                 │  │               │
│  │  └─────────────────────────────────────────────────────────────────┘  │               │
│  └───────────────────────────────────────────────────────────────────────┘               │
│                                                                                          │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. API Layer (FastAPI)

**Process:** `uvicorn app.main:app` (development) / `gunicorn -k UvicornWorker` (production)
**Port:** 8000 (internal) → 18420 (host)

The API layer is the single entry point for all client interactions. Built with the factory pattern (`app.factory.create_app()`), it initializes:

- CORS middleware (configured via `BACKEND_CORS_ORIGINS`)
- Router tree under `/api/v1/`
- Health check at `/health`
- Alembic migrations on startup (via entrypoint.sh)
- Database seeding (via `app.db.seed`)

**Route tree:**
```
/api/v1/
├── /workers/
│   ├── POST   /dispatch          → create task + queue to Celery
│   ├── POST   /heartbeat         → register/update worker
│   ├── GET    /status            → list all workers
│   └── WS     /{worker_id}/ws   → real-time log stream
├── /tasks/
│   ├── GET    /                  → list tasks (paginated)
│   └── GET    /{id}              → task detail with result
├── /identities/
│   ├── POST   /register          → create new identity
│   ├── POST   /best-match        → get best identity by vector similarity
│   └── GET    /                  → list all identities
├── /proxies/
│   └── GET    /health            → proxy pool status
└── /stats/
    └── GET    /                  → dashboard metrics
```

**Request/Response contracts:** All endpoints use Pydantic v2 schemas (`app.schemas.*`) for validation and serialization. `TaskType` and `TaskStatus` are string enums enforced at the API boundary.

---

### 2. Task Queue (Celery + Redis)

**Broker/Backend:** Redis (single instance, password-protected)
**Serialization:** JSON (default Celery serializer)
**Concurrency model:** prefork (multi-process)

**Queue topology:**
```
Redis :6379/0
├── browser-queue    → browser automation tasks (view_boost, profile_boost)
├── mobile-queue     → physical device tasks (warmup)
└── celery           → default queue (fallback)
```

**Routing rules** (defined in `app.core.celery_app`):
```python
task_routes = {
    "app.tasks.mobile.*": {"queue": "mobile-queue"},
    "app.tasks.browser.*": {"queue": "browser-queue"},
}
```

**Task discovery:** `celery_app.autodiscover_tasks(["app.tasks"])` scans `app/tasks/__init__.py` which explicitly imports all task functions to ensure registration.

**Registered tasks:**
| Task Name | Function | Queue |
|-----------|----------|-------|
| `app.tasks.browser.view_boost` | `browser_view_boost()` | browser-queue |
| `app.tasks.browser.profile_boost` | `browser_profile_boost()` | browser-queue |
| `app.tasks.mobile.warmup` | `mobile_warmup()` | mobile-queue |

**Task base class:**
```python
class TaskWithDB(CeleryTask):
    def get_session(self):
        return Session(engine)
```
All tasks inherit `TaskWithDB` for database access within the Celery process. Sessions are created per-task invocation via context manager (`with self.get_session() as session:`).

---

### 3. Database Layer (PostgreSQL 16 + pgvector)

**ORM:** SQLModel (SQLAlchemy 2.0 + Pydantic hybrid)
**Migrations:** Alembic (auto-run on backend startup)
**Connection pooling:** `pool_size=10, max_overflow=20, pool_pre_ping=True`

**Schema:**
```
identities
├── id              SERIAL PRIMARY KEY
├── username        VARCHAR(255) UNIQUE, INDEXED
├── platform        VARCHAR(50)          — "tiktok", "youtube"
├── status          VARCHAR(20)          — "active", "suspended"
├── user_agent      TEXT                 — real browser UA string
├── screen_resolution VARCHAR(20)        — "1920x1080", "390x844"
├── behavioral_dna  VECTOR(1536)         — pgvector embedding
├── trust_score     INT DEFAULT 50       — 0-100 platform trust
├── last_used_at    TIMESTAMPTZ          — cooldown tracking
└── created_at      TIMESTAMPTZ

workers
├── id              SERIAL PRIMARY KEY
├── name            VARCHAR(255) UNIQUE
├── type            VARCHAR(50)          — "LXC-Selenium", "Physical-S24"
├── status          VARCHAR(20)          — "IDLE", "BUSY", "ERROR"
├── ip_address      VARCHAR(45)
└── last_heartbeat  TIMESTAMPTZ

tasks
├── id              SERIAL PRIMARY KEY
├── type            VARCHAR(50)          — TaskType enum value
├── target_url      TEXT
├── status          VARCHAR(20)          — PENDING/QUEUED/RUNNING/SUCCESS/FAILED
├── config          JSONB                — {volume, max_videos, parent_task_id}
├── celery_task_id  VARCHAR(255)
├── worker_id       INT → workers(id)
├── started_at      TIMESTAMPTZ
├── completed_at    TIMESTAMPTZ
├── error_message   TEXT
├── result          JSONB                — {views_delivered, videos_found, child_task_ids}
├── created_at      TIMESTAMPTZ
└── updated_at      TIMESTAMPTZ

proxies
├── id              SERIAL PRIMARY KEY
├── ip_address      VARCHAR(45)
├── port            INT
├── protocol        VARCHAR(10)          — "socks5", "http"
├── provider        VARCHAR(50)          — "Digi RO", "Orange RO"
├── is_active       BOOLEAN
└── last_rotated_at TIMESTAMPTZ
```

**pgvector usage:** The `behavioral_dna` column stores 1536-dimensional float vectors. Identity selection queries use `l2_distance()` to find the most behaviorally-similar identity for a given task context, preventing repeated identical interaction patterns.

---

### 4. Identity Mesh Service

**Purpose:** Select the optimal fake user profile for each task execution.

**Assignment strategy:** Round-robin pre-assignment at dispatch/fan-out time (not at worker execution time). This eliminates race conditions between parallel workers competing for the same identity.

- **Single video dispatch:** API endpoint calls `get_best_identity_for_task()` and passes `identity_id` to Celery
- **Profile boost fan-out:** Orchestrator fetches all available identities, assigns round-robin across child tasks
- **Worker execution:** Receives `identity_id` kwarg, loads by primary key — no search, no race

**Selection algorithm (used at dispatch time):**
```
1. Filter: platform match + status="active" + behavioral_dna NOT NULL
2. Filter: last_used_at IS NULL OR last_used_at < (now - 2 hours)
3. Order:  L2 distance between target_vector and behavioral_dna ASC
4. Limit:  1
5. Fallback: if no vector matches, select any active identity not on cooldown
             ordered by last_used_at ASC NULLS FIRST
```

**Round-robin fan-out (profile boost):**
```
_get_available_identities(session, "tiktok")  → [id_A, id_B, ..., id_T]

for i, (video_url, view_num) in enumerate(all_tasks):
    identity = identities[i % len(identities)]
    → child task config: {identity_id, identity_username}
    → Celery kwargs: {identity_id: identity.id}
```

**Auditability:** Each task's `config` JSON records `identity_id` and `identity_username` at dispatch time. The `result` JSON records `identity_used` on completion. This enables full traceability: which identity viewed which video, when.

**Cooldown mechanism:** After a task completes successfully, `IdentityMeshService.mark_identity_used()` sets `last_used_at = now()`. The identity becomes unavailable for 2 hours. This prevents TikTok from seeing the same "user" generating suspicious activity patterns.

**Seeding:** `app.db.seed` generates identities with:
- Realistic Romanian name patterns (30 first names × 20 last names × 10 username patterns)
- Diverse real-world user agents (Chrome/Firefox/Safari, desktop/mobile, Windows/Mac/Linux/Android/iOS)
- Random screen resolutions matching the UA platform
- Pre-generated 1536-dim behavioral DNA vectors

---

### 5. Platform Driver Framework

**Pattern:** Abstract Base Class with per-platform implementations

```python
PlatformDriver (ABC)
├── __init__(worker_id, log_callback)
├── log(message) → async, broadcasts to WebSocket if callback set
├── execute_view(url, identity, proxy) → bool     [abstract]
└── execute_warmup(identity, duration) → bool      [abstract]
```

**Driver Registry:**
```python
DRIVER_REGISTRY = {
    "tiktok_views":         TikTokBrowserDriver,
    "tiktok_profile_boost": TikTokBrowserDriver,
    "tiktok_warmup":        TikTokBrowserDriver,
    "yt_watchtime":         YouTubeBrowserDriver,
}

def get_driver(task_type, worker_id, log_callback=None) -> PlatformDriver
```

**TikTokBrowserDriver execution flow:**
```
execute_view(url, identity, proxy):
  1. Launch Chromium (headless, stealth flags)
     - --disable-blink-features=AutomationControlled
     - playwright-stealth v2 (Stealth.apply_stealth_async)
     - Custom viewport (1920×1080), locale (en-US), timezone (Europe/Bucharest)
     - Proxy binding if proxy provided

  2. Navigate to URL (follows redirects for vm.tiktok.com short links)
     - wait_until="domcontentloaded" (not networkidle — TikTok never stops loading)

  3. Dismiss popups
     - Cookie consent: scans 5 selector variants
     - Login modal: scans 3 close-button selectors

  4. Verify video playback
     - Wait for <video> element in DOM
     - Check video.paused === false && video.readyState >= 2
     - Click video to trigger play if needed
     - Poll up to 15 seconds for playback confirmation

  5. Duration-aware watching
     - Read video.duration from DOM
     - Watch 70-110% of duration (randomized), cap 90s, min 5s
     - Fallback to 10-45s random dwell if duration unavailable
     - Periodically verify playback, click to resume if auto-paused

  6. Behavioral humanization (BehavioralDNA)
     - Bezier-curved scroll (3-8 steps, horizontal jitter)
     - Curiosity actions (weighted random):
       55% nothing, 20% check comments, 15% like, 10% pause/unpause
     - Actions use real TikTok DOM selectors ([data-e2e="like-icon"], etc.)

  7. Cleanup: close browser, return success/failure
```

**Profile scraping flow (`scrape_profile_videos`):**
```
  1. Launch stealth browser (no identity/proxy needed — just reading public data)
  2. Navigate to profile URL
  3. Dismiss popups
  4. Scroll 3 times to load video grid (lazy-loaded)
  5. Extract all <a href="/video/..."> links from DOM
  6. Deduplicate and limit to max_videos (default 20)
  7. Return list of full video URLs
```

---

### 6. Worker Deployment

**Docker Worker (UM680):** Runs inside the Docker Compose stack as a Celery worker container. Uses the same image as the backend but with a different entrypoint (`celery -A app.core.celery_app:celery_app worker`). Code is volume-mounted for hot-reload in development.

**LXC Workers (HP Z420 / Proxmox):** Provisioned via Ansible playbooks:

| Playbook | Purpose |
|----------|---------|
| `setup-worker.yml` | Full provisioning: apt deps, Chrome, Python venv, Playwright, systemd service, code sync |
| `deploy-code.yml` | Fast code-only rsync + service restart |

**LXC Worker runtime:**
```
/opt/tg-worker/
├── venv/                    — Python 3.12 virtualenv
├── app/                     — synced from backend/app/ via rsync
├── config/.env              — REDIS_URL, DATABASE_URL, WORKER_NAME
└── start-worker.sh          — activates venv, exports env, exec celery
```

**systemd service (`tg-worker.service`):**
```ini
[Service]
Type=simple
ExecStart=/opt/tg-worker/start-worker.sh
Restart=on-failure
RestartSec=10
Environment=PYTHONPATH=/opt/tg-worker
```

**Cross-VLAN connectivity:**
```
LXC Worker (10.10.10.106, VLAN 10)
    → Redis    at 10.20.20.200:18425 (VLAN 20, via MikroTik routing)
    → Postgres at 10.20.20.200:18424 (VLAN 20, via MikroTik routing)
```
MikroTik firewall rule 0 allows UM680 (10.20.20.200) → MGMT VLAN (10.10.10.0/24). Workers initiate outbound connections to the control plane — no inbound rules needed on VLAN 10.

---

### 7. WebSocket Real-Time Logging

**Server:** `ConnectionManager` singleton in `app.core.websocket`
**Protocol:** Native WebSocket via FastAPI at `/api/v1/workers/{worker_id}/ws`
**Client:** React `LiveConsole` component connects through nginx proxy

**Data flow:**
```
Worker executes task
  → driver.log("Navigating to URL...")
    → PlatformDriver._log_callback(message)
      → ConnectionManager.broadcast_to_worker(message, worker_id)
        → WebSocket.send_text() to all connected clients for that worker_id

Browser dashboard
  → LiveConsole connects: ws://host:18423/api/workers/{id}/ws (via nginx)
    → receives log lines, renders in terminal-style UI (max 50 lines, auto-scroll)
```

---

### 8. Security Model

**Network isolation:**
- VLAN 20 (GRID): Control plane only — UM680
- VLAN 10 (MGMT): Workers + infrastructure — HP Z420, Proxmox VMs
- VLAN 30 (TRUSTED): Personal devices via WiFi (no TrafficGrid access)
- MikroTik firewall drops VLAN 20 → VLAN 30 (grid cannot reach personal devices)

**Credentials:**
- PostgreSQL: strong hex password (64 chars), no defaults
- Redis: `requirepass` with strong hex password
- All credentials in `.env` (gitignored) and Ansible vault-ready secrets file
- Docker Compose interpolates from env vars — no hardcoded passwords

**Authentication:** None yet on API endpoints (planned for Phase 2).

---

### 9. Configuration

**Environment-driven** via `pydantic-settings.BaseSettings`:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | assembled from parts | PostgreSQL connection string |
| `POSTGRES_SERVER` | `db` | DB hostname (Docker service name) |
| `POSTGRES_PORT` | `5432` | DB port |
| `POSTGRES_USER` | `admin` | DB user |
| `POSTGRES_PASSWORD` | `password` | DB password |
| `POSTGRES_DB` | `trafficgrid` | DB name |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection (broker + backend) |
| `BACKEND_CORS_ORIGINS` | `["*"]` | Allowed CORS origins |
| `ENV` | `development` | Controls hot-reload vs gunicorn |

`DATABASE_URL` is assembled automatically via `model_validator` if not provided explicitly — allowing either full URL or individual parts.

---

### 10. Port Map

| Port | Service | Protocol | Exposed To |
|------|---------|----------|-----------|
| 18420 | FastAPI backend | HTTP/WS | Host + LAN |
| 18421 | SOCKS5 proxy gateway | TCP | Host + LAN |
| 18422 | Gateway management API | HTTP | Host + LAN |
| 18423 | nginx (React SPA + API proxy) | HTTP | Host + LAN |
| 18424 | PostgreSQL | TCP | Host + LAN (workers) |
| 18425 | Redis | TCP | Host + LAN (workers) |
