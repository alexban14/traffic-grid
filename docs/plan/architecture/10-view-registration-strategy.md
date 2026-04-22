# 10 — View Registration Strategy

**Last Updated:** 2026-04-22
**Status:** Path B (anonymous persistence) in progress, Path A (authenticated accounts) planned

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

### Path A — Authenticated Accounts (Fallback if Path B Fails)

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

| Phase | What | When | Depends On |
|-------|------|------|-----------|
| **B1** | Profile persistence (cookies save/load) | Now | Nothing |
| **B2** | FYP warm-up task | Now | B1 |
| **B3** | FYP browse before target navigation | Now | B1 |
| **B4** | Test: do anonymous persistent views count? | After B1-B3 | B3 |
| **A1** | Schema + API for authenticated accounts | After B4 fails | B4 result |
| **A2** | ADB phone setup on HP Z420 | After A1 | USB hub + phones |
| **A3** | Account creation automation (Appium) | After A2 | A2 |
| **A4** | Cookie export from physical devices | After A3 | A3 |
| **A5** | Import flow + session health checks | After A4 | A4 |
| **A6** | Full authenticated view pipeline test | After A5 | A5 |

---

## Decision Point

After implementing Path B (B1-B4), test with 10 views on a video with a known view count:

- **Views appear within 30 min** → Path B works, continue with anonymous persistence
- **Views don't appear** → Move to Path A, start account sourcing

Document the test results here:

### Path B Test Results

| Date | Video | Views Before | Views After (30min) | Views After (24hr) | Result |
|------|-------|-------------|--------------------|--------------------|--------|
| | | | | | |
