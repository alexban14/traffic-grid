# 10 — View Registration Strategy

**Last Updated:** 2026-04-22
**Status:** Path B tested and FAILED. Dual-path architecture implementing both A + B with runtime selection.

---

## Problem Statement

TrafficGrid successfully navigates to TikTok videos, verifies playback, watches for realistic durations, and performs behavioral interactions — but **views are not registering** on TikTok's view counter.

### Root Cause Analysis

TikTok's view counting requires more than a `<video>` element playing:

| Factor | Current State | Impact |
|--------|--------------|--------|
| **Session cookies** | Fresh browser every time — no cookies | Critical: TikTok discards views from unknown sessions |
| **Anonymous visitor ID** | No `tt_webid` cookie persisted | High: TikTok can't track the "viewer" across requests |
| **Analytics SDK** | May not fire without proper session | High: Internal tracking events may not register |
| **Account login** | Not logged in | Medium: Anonymous views may count but at lower weight |
| **IP diversity** | Single ISP IP for all workers | Medium: Deduplication per IP |
| **Headless detection** | Using headless Chromium | Low: Stealth plugin mitigates most checks |

---

## Strategy: Two-Path Approach

### Path B — Anonymous Session Persistence (Implement First)

**Goal:** Maintain persistent browser profiles per identity so TikTok sees "returning visitors" instead of fresh anonymous sessions.

**How it works:**

```
Identity "andrei.pop95" — first use:
  1. Fresh Chromium launches
  2. Browse TikTok FYP for 30-60s (warm-up)
  3. TikTok sets cookies: tt_webid, tt_chain_token, ttwid, etc.
  4. Navigate to target video, watch it
  5. Save all cookies + localStorage to profiles/andrei.pop95/

Identity "andrei.pop95" — subsequent uses:
  1. Chromium launches, loads saved profile from profiles/andrei.pop95/
  2. TikTok recognizes returning visitor via tt_webid cookie
  3. Browse FYP briefly (10-20s) to refresh session
  4. Navigate to target video, watch it
  5. Update saved profile with new cookies
```

**Implementation (COMPLETED 2026-04-22):**

| Component | Status | Details |
|-----------|--------|---------|
| `ProfileManager` service | Done | `app.services.profile_manager` — save/load Playwright `storage_state()` |
| `TikTokBrowserDriver` | Done | `_create_context()` loads profile, `_save_profile()` saves after view |
| `browser_warmup` Celery task | Done | `app.tasks.browser.warmup` — explicit FYP browse for N minutes |
| `execute_view` auto-warmup | Done | First use: 3 FYP videos, returning: 1 FYP video before target |
| Docker volume | Done | `./profiles:/app/profiles` mounted on worker container |
| LXC workers | Pending | Profiles created locally; need rsync/NFS for shared profiles |

**Two warmup modes:**

1. **Explicit warmup** — dispatch `tiktok_warmup` task, browses FYP for N minutes
   ```
   POST /dispatch {"task_type": "tiktok_warmup", "target_url": "warmup", "volume": 3}
   → volume = minutes of FYP browsing
   → warms up 1 identity (pre-assigned at dispatch)
   ```

2. **Auto-warmup on first view** — built into `execute_view`, no separate task needed
   ```
   Identity has no saved profile → browse 3 FYP videos (10-30s each) before target
   Identity has saved profile → browse 1 FYP video (5-15s) as session refresh
   ```

Most use cases don't need explicit warmup. The auto-warmup handles it transparently — every identity gets warmed on first use and refreshed on subsequent uses.

**Profile storage structure:**
```
profiles/                          # gitignored, Docker volume mounted
├── tiktok/
│   ├── andrei.pop95/
│   │   ├── state.json            # Playwright storage_state (cookies + localStorage)
│   │   └── metadata.json         # Last saved timestamp
│   ├── maria_ionescu/
│   │   └── ...
│   └── ...
└── youtube/
    └── ...
```

**Auto-warmup sequence (first use of identity via execute_view):**
```
1. Launch stealth browser with identity's user agent
2. Check ProfileManager: no saved profile exists
3. Navigate to https://www.tiktok.com/foryou
4. Dismiss cookie consent + login popups
5. Watch 3 random FYP videos (10-30s each, occasional like at 10% chance)
6. TikTok sets cookies: tt_webid, tt_chain_token, ttwid, etc.
7. Navigate to target video URL
8. Watch with BehavioralDNA (duration-aware, interactions)
9. Save cookies + localStorage via Playwright storage_state → profiles/tiktok/<username>/state.json
```

**Returning identity sequence (subsequent uses via execute_view):**
```
1. Launch stealth browser, load saved cookies from profile
2. Navigate to https://www.tiktok.com/foryou
3. Verify cookies are active (tt_webid present)
4. Watch 1-2 FYP videos (10-20s) to refresh session
5. Navigate to target video
6. Watch with BehavioralDNA (duration-aware, interactions)
7. Save updated cookies back to profile
```

**Success criteria:** Views start appearing on TikTok's counter within 30 minutes of execution.

**Timeline:** 1-2 days implementation

---

---

## Dual-Path Architecture (Runtime Selectable)

Both paths coexist in the same system. The `account_type` field on each identity determines which path is used. The dispatch request includes an optional `account_type` parameter to filter identity selection.

```
Identity Pool
├── anonymous (Path B)     → FYP-warmed cookies, no login
│   └── Lower trust, free, unlimited creation
│
└── authenticated (Path A) → Real TikTok session cookies
    └── Higher trust, requires account + SIM, limited pool

Dispatch Request:
  POST /dispatch {
    "task_type": "tiktok_views",
    "target_url": "...",
    "volume": 5,
    "account_type": "authenticated"    ← optional, defaults to "any"
  }

  account_type options:
    "authenticated" → only use logged-in identities
    "anonymous"     → only use anonymous identities
    "any" (default) → prefer authenticated, fall back to anonymous
```

**Why both paths:**
- Anonymous identities are free, unlimited, and useful for low-value tasks (profile scraping, feed simulation)
- Authenticated identities are scarce and valuable — used for actual view generation
- The system gracefully falls back: if no authenticated identities are available, it can use anonymous ones
- Allows A/B testing: dispatch same video with both types, compare registration rates

---

### Path A — Authenticated Accounts

**Goal:** Log into real TikTok accounts, giving each identity maximum platform trust.

**Why this is harder:**
- Need real TikTok accounts (creation requires phone number + verification)
- Accounts can be banned if detected
- Login flow involves CAPTCHA, 2FA, phone verification
- Account management (creation, warm-up, rotation, recovery) is a full subsystem

**Account Sourcing Strategy:**

| Method | Cost | Trust Level | Risk | Scalability |
|--------|------|-------------|------|-------------|
| **Manual creation** | Free (time) | Highest | Low (human-created) | Low (5-10/day) |
| **Physical phone farm** | Medium (devices + SIMs) | Highest | Low | Medium (1 per device) |
| **Purchased accounts** | $0.50-5/account | Medium | High (may be flagged) | High |
| **SMS verification services** | $0.10-0.50/verification | Medium | Medium | High |

**Recommended approach: Physical phone farm for account creation, browser farm for view execution.**

1. Create accounts on physical devices (S24 Ultra, A40, Moto G40, P10)
2. Warm up accounts manually for 3-5 days (real usage)
3. Export session cookies from the device
4. Import cookies into browser worker identities
5. Execute views from browser workers with authenticated sessions

**Account Lifecycle:**

```
┌─────────────────────────────────────────────────────────┐
│                   ACCOUNT LIFECYCLE                       │
│                                                           │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│  │ CREATION │───►│ WARM-UP  │───►│  ACTIVE  │──┐        │
│  │          │    │ (3-5 days)│    │          │  │        │
│  │ Phone +  │    │ Browse   │    │ Session  │  │        │
│  │ SIM card │    │ FYP, like│    │ exported │  │        │
│  │ required │    │ follow   │    │ to worker│  │        │
│  └──────────┘    └──────────┘    └─────┬────┘  │        │
│                                        │       │        │
│                                        ▼       │        │
│                                  ┌──────────┐  │        │
│                                  │ COOLDOWN │  │        │
│                                  │ (2-24 hrs)│  │        │
│                                  └─────┬────┘  │        │
│                                        │       │        │
│                                        └───────┘        │
│                                                          │
│  ┌──────────┐    ┌──────────┐                           │
│  │ FLAGGED  │───►│ RECOVERY │──► back to ACTIVE or      │
│  │ (captcha │    │ (phone   │    SUSPENDED                │
│  │  or ban) │    │  verify) │                            │
│  └──────────┘    └──────────┘                           │
│                                                          │
│  ┌──────────┐                                           │
│  │SUSPENDED │  Permanently banned, replace with new      │
│  └──────────┘                                           │
└─────────────────────────────────────────────────────────┘
```

**Database schema additions for Path A:**

```sql
ALTER TABLE identities ADD COLUMN account_type VARCHAR(20) DEFAULT 'anonymous';
-- 'anonymous' = Path B (cookies only)
-- 'authenticated' = Path A (logged-in TikTok account)

ALTER TABLE identities ADD COLUMN phone_number VARCHAR(20);
ALTER TABLE identities ADD COLUMN email VARCHAR(255);
ALTER TABLE identities ADD COLUMN account_status VARCHAR(20) DEFAULT 'active';
-- 'creating', 'warming_up', 'active', 'cooldown', 'flagged', 'suspended'

ALTER TABLE identities ADD COLUMN warmup_completed_at TIMESTAMPTZ;
ALTER TABLE identities ADD COLUMN flagged_at TIMESTAMPTZ;
ALTER TABLE identities ADD COLUMN flag_reason TEXT;
```

**New API endpoints for Path A:**

```
POST /api/v1/identities/import-session
  → Import cookies from a physical device into an identity profile
  Body: { identity_id, cookies_json, source_device }

POST /api/v1/identities/warmup
  → Trigger a warmup task for an identity (browse FYP, build trust)
  Body: { identity_id, duration_mins }

GET /api/v1/identities/{id}/health
  → Check if session is still valid (try loading TikTok with saved cookies)
  Returns: { logged_in: bool, cookies_valid: bool, last_activity }

POST /api/v1/identities/{id}/recover
  → Mark identity as flagged, trigger recovery flow
```

**Physical Device Integration (ADB/Appium):**

```
1. Connect phone to HP Z420 via USB hub
2. ADB opens TikTok app
3. uiautomator2 performs account creation:
   - Enter phone number (Romanian SIM)
   - Receive SMS verification code
   - Set username, profile picture
   - Accept terms
4. Warm-up phase (automated via Appium):
   - Browse FYP for 30 min/day for 3-5 days
   - Like 5-10 videos per session
   - Follow 2-3 creators per day
   - Watch videos to completion
5. Export session:
   - Extract cookies from TikTok app WebView
   - Or use Chrome on device, log in, export cookies
6. Import to worker identity:
   - POST /api/v1/identities/import-session
```

**Account pool sizing for Path A:**

| Scale Target | Accounts Needed | Views/Account/Day | Cooldown |
|-------------|----------------|-------------------|----------|
| 1,000 views/day | 20-50 accounts | 20-50 | 4-8 hours |
| 10,000 views/day | 100-200 accounts | 50-100 | 2-4 hours |
| 100,000 views/day | 500-1000 accounts | 100-200 | 1-2 hours |

**Romanian SIM card strategy:**
- Orange Romania prepaid: ~€5/SIM, SMS verification works
- Digi Romania: ~€3/SIM, cheapest option
- Vodafone Romania: ~€5/SIM, wide coverage
- Buy 20-50 SIMs initially, rotate for account creation
- Each SIM can create 2-3 accounts before TikTok flags it

---

## Implementation Timeline

| Phase | What | Status | Notes |
|-------|------|--------|-------|
| **B1** | Profile persistence (cookies save/load) | DONE | Playwright storage_state per identity |
| **B2** | FYP warm-up task | DONE | browser_warmup Celery task |
| **B3** | FYP browse before target navigation | DONE | Auto-warmup on first view (3 FYP videos) |
| **B4** | Test: do anonymous persistent views count? | FAILED | Views not registered after 24 hours |
| **D1** | Dual-path: add account_type to Identity model + migration | In Progress | |
| **D2** | Dual-path: account_type filter in identity selection | In Progress | |
| **D3** | Dual-path: account_type param in dispatch request | In Progress | |
| **D4** | Manual session import endpoint | In Progress | Import cookies from manual browser login |
| **D5** | Session health check endpoint | In Progress | Verify if saved session is still logged in |
| **D6** | Test: manually log in, export cookies, import, dispatch views | Next | |
| **A1** | ADB phone setup on HP Z420 | Planned | USB hub + phones |
| **A2** | Account creation automation (Appium) | Planned | After A1 |
| **A3** | Automated cookie export from physical devices | Planned | After A2 |

---

## Path B Test Results

| Date | Video | Views Before | Views After (24hr) | Result |
|------|-------|-------------|--------------------| --------|
| 2026-04-22 | @transylvania_trails (5 videos, 10 views total) | Noted | No change | FAILED — anonymous sessions not counted |

**Conclusion:** TikTok does not count views from anonymous browser sessions, even with persistent cookies, FYP pre-browse, and stealth. **Authenticated accounts required for view registration.**

---

## Dual-Path Implementation Plan (D1-D6)

### D1: Identity Model Changes

```sql
ALTER TABLE identities ADD COLUMN account_type VARCHAR(20) DEFAULT 'anonymous';
-- 'anonymous' = Path B (FYP cookies only, no login)
-- 'authenticated' = Path A (logged-in TikTok session)

ALTER TABLE identities ADD COLUMN account_status VARCHAR(20) DEFAULT 'active';
-- 'active', 'cooldown', 'flagged', 'suspended'
-- (existing 'status' field kept for backwards compat)
```

### D2: Identity Selection with account_type Filter

```python
# In identity_mesh.py — get_best_identity_for_task():
# New param: account_type: Optional[str] = None
#   "authenticated" → only authenticated identities
#   "anonymous" → only anonymous identities
#   "any" or None → prefer authenticated, fall back to anonymous
```

### D3: Dispatch Request Schema Update

```python
class DispatchRequest(BaseModel):
    task_type: TaskType
    target_url: str
    volume: int = 1
    drip_minutes: Optional[int] = None
    account_type: Optional[str] = None  # "authenticated", "anonymous", or None (any)
```

### D4: Manual Session Import Endpoint

```
POST /api/v1/identities/import-session
Body: {
  "username": "real_tiktok_user",
  "platform": "tiktok",
  "cookies_json": "[{\"name\": \"sessionid\", \"value\": \"...\", ...}]",
  "user_agent": "Mozilla/5.0 ..."
}

Flow:
1. Create or update identity with account_type = "authenticated"
2. Save cookies_json as Playwright storage_state format to profiles/tiktok/<username>/state.json
3. Return identity_id
```

**How to get cookies manually:**
1. Open Chrome, go to TikTok, log in manually
2. Open DevTools → Application → Cookies → copy all TikTok cookies
3. Or use a browser extension like "EditThisCookie" to export as JSON
4. POST to /import-session with the cookies

### D5: Session Health Check

```
GET /api/v1/identities/{id}/health

Flow:
1. Load saved profile for the identity
2. Launch stealth browser with profile
3. Navigate to https://www.tiktok.com
4. Check if user menu / avatar is visible (indicates logged in)
5. Return { "logged_in": true/false, "cookies_valid": true/false }
```

### D6: End-to-End Test

1. Manually create a TikTok account on phone
2. Log into TikTok in Chrome on dev machine
3. Export cookies via DevTools
4. Import via POST /import-session
5. Dispatch a view task with account_type="authenticated"
6. Check if view registers within 30 minutes
