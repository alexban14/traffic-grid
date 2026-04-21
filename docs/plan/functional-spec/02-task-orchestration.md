# 02 — Task Orchestration & Workflow

## Overview

TrafficGrid uses a distributed state machine to manage tasks. Unlike simple scripts, a TrafficGrid task is a multi-stage workflow that can recover from platform-specific interruptions (captchas, slow loads).

---

## The "Human-Mimic" Workflow

Every view/engagement task follows these logical steps:

### Stage 1: Preparation
- **Worker Assignment**: Control Plane selects an available LXC/Device based on platform target.
- **Network Binding**: MeLe Gateway assigns a proxy.
- **Profile Injection**: Browser/App profile (cookies, UA) is injected into the worker.

### Stage 2: Navigation (Humanized)
- **Direct Link vs. Search**: 20% of tasks use search results to find the video; 80% use direct links.
- **Undetected Load**: `undetected-chromedriver` initializes the browser.
- **Scroll-to-View**: Content is not viewed until it is "scrolled into the viewport" naturally.

### Stage 3: Engagement
- **Watch Time**: Calculated as `video_duration * random(0.7, 1.1)`.
- **Secondary Actions**: Optional like/share/comment based on task config.
- **Retention Modeling**: Ensuring the "video played" signal is sent to platform analytics via natural interaction.

### Stage 4: Cleanup & Reporting
- **Cookie Save**: Current session state is persisted back to PostgreSQL.
- **Success Signal**: Metrics (watch time, IP used) are reported to Control Plane.
- **Proxy Release**: IP is returned to the pool or flagged for rotation.

---

## Priority & Queue Management

Tasks are prioritized based on:
1. **Premium Accounts**: High-trust accounts get priority for engagement.
2. **Freshness**: New videos (first 2 hours) get burst-view priority to trigger algorithmic discovery.
3. **Recovery**: Re-attempts for failed tasks due to proxy issues.

---

## Platform-Specific Logic

| Platform | Key Detection Point | TrafficGrid Solution |
|----------|---------------------|----------------------|
| **TikTok** | WebGL Fingerprint | Custom JS injection to spoof hardware acceleration. |
| **YouTube**| Google Account Trust| Slow account warming; using physical devices for "Prime" views. |
| **Instagram**| Mouse Movement | Bezier-curved interaction paths. |
