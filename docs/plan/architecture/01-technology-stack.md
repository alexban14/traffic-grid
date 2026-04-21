# 01 — Technology Stack Decision

---

## Control Plane — Python FastAPI

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| **Framework** | FastAPI | 0.110+ | Asynchronous native, high performance for I/O bound task orchestration. |
| **Runtime** | Python | 3.12+ | Best ecosystem for automation (Selenium, Appium) and AI integration. |
| **Task Queue** | Celery + Redis | 5.3+ | Reliable distributed task processing for worker plane communication. |
| **API Spec** | OpenAPI (Swagger) | Auto | Built-in interactive documentation for easier frontend integration. |

### Why FastAPI over Laravel for TrafficGrid

- **Automation Ecosystem**: Selenium and Appium have first-class Python support.
- **Asynchronous I/O**: Efficiently managing hundreds of concurrent worker heartbeats and proxy health checks.
- **`ai.dok` Alignment**: Matches existing project architecture for consistency in deployment patterns.

---

## Worker Plane — Selenium & Appium

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Web Driver** | Selenium (undetected-chromedriver) | Core automation for TikTok/YouTube web views; fingerprinting bypass. |
| **Mobile Driver** | Appium + ADB | Physical device automation for highest-trust engagement. |
| **Orchestration** | Python Workers | Local agents running inside LXC containers on HP Z420. |

### Anti-Detection Stack

- **undetected-chromedriver**: Essential for bypassing Cloudflare and social platform browser checks.
- **WebGL/Canvas Noise**: Custom JavaScript injection to randomize browser hardware signatures.
- **Stealth Plugins**: Masking Selenium's `navigator.webdriver` property.

---

## Proxy Mesh & Networking

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Proxy Gateway** | MeLe Quieter3Q | Dedicated, fanless hardware for 24/7 proxy gateway uptime. |
| **Orchestration** | Proxidize / Custom Python | Management of 4G/5G mobile dongles and residential rotations. |
| **Protocol** | SOCKS5 / HTTP | Universal support for Selenium and system-wide routing. |

---

## Data Layer

| Store | Technology | Purpose |
|-------|-----------|---------|
| **Primary DB** | PostgreSQL 16 | Relational data for tasks, devices, and proxy health. |
| **Vector DB** | pgvector | Storing behavioral embeddings to mimic real human interaction paths. |
| **Cache** | Redis 7 | Task queue, heartbeat storage, and real-time status updates. |

---

## Frontend — React Dashboard

| Technology | Rationale |
|-----------|-----------|
| **React 19** | Component-driven UI for device and task management. |
| **TanStack Router** | Type-safe routing for complex dashboard layouts. |
| **TanStack Query** | Efficient caching and synchronization of worker statuses. |
| **Zod** | Runtime schema validation for task configuration payloads. |
| **Tailwind CSS** | Rapid UI development with consistent styling. |
